#include "DirectionalCorrection.h"
#include <vector>


DirectionalCorrection::DirectionalCorrection()
{
}

void DirectionalCorrection::Init(int res, std::string &xml, std::string &scatcoef,
                                 InputImageType2::Pointer &cldImg, InputImageType2::Pointer &watImg,
                                 InputImageType2::Pointer &snowImg, InputImageType1::Pointer &angles,
                                 InputImageType2::Pointer &ndvi)
{
    m_nRes = res;
    m_strXml = xml;
    m_strScatCoeffs = scatcoef;

    m_AnglesImg = angles;
    m_NdviImg = ndvi;
    m_CSM = cldImg;
    m_WM = watImg;
    m_SM = snowImg;

    m_ImageList = ImageListType::New();
    m_Concat = ListConcatenerFilterType::New();
}

void DirectionalCorrection::DoExecute()
{
    auto factory = MetadataHelperFactory::New();
    auto pHelper = factory->GetMetadataHelper(m_strXml, m_nRes);
    //float fReflQuantifValue = pHelper->GetReflectanceQuantificationValue();
    std::string inputImageFile = pHelper->GetImageFileName();
    m_inputImageReader = ReaderType::New();
    m_inputImageReader->SetFileName(inputImageFile);
    m_inputImageReader->UpdateOutputInformation();

    InputImageType1::Pointer inputImg = m_inputImageReader->GetOutput();
    extractBandsFromImage(inputImg);

    // extract the cloud, water and snow masks from the masks file
    m_ImageList->PushBack(m_CSM);
    m_ImageList->PushBack(m_SM);
    m_ImageList->PushBack(m_WM);
    m_ImageList->PushBack(m_NdviImg);
    extractBandsFromImage(m_AnglesImg);

    m_Concat->SetInput(m_ImageList);

    std::vector<ScaterringFunctionCoefficients> scatteringCoeffs;
    scatteringCoeffs = loadScatteringFunctionCoeffs(m_strScatCoeffs);
    unsigned int nBandsForRes = pHelper->GetBandsNoForCurrentResolution();
    if(nBandsForRes != scatteringCoeffs.size()) {
        itkExceptionMacro("Scattering coefficients file contains only " << scatteringCoeffs.size()
                          << " but are expected coefficients for " << nBandsForRes << " bands!");
    }

    m_Functor.Initialize(scatteringCoeffs);
    m_DirectionalCorrectionFunctor = FunctorFilterType::New();
    m_DirectionalCorrectionFunctor->SetFunctor(m_Functor);
    m_DirectionalCorrectionFunctor->SetInput(m_Concat->GetOutput());
    m_DirectionalCorrectionFunctor->UpdateOutputInformation();
    m_DirectionalCorrectionFunctor->GetOutput()->SetNumberOfComponentsPerPixel(scatteringCoeffs.size());
}

int DirectionalCorrection::extractBandsFromImage(InputImageType1::Pointer & imageType) {
    int nbBands = imageType->GetNumberOfComponentsPerPixel();
    for(int j=0; j < nbBands; j++)
    {
        // extract the band without resampling
        m_ImageList->PushBack(m_ResampledBandsExtractor.ExtractResampledBand(imageType, j+1));
    }
    return nbBands;
}

std::vector<ScaterringFunctionCoefficients> DirectionalCorrection::loadScatteringFunctionCoeffs(std::string &strFileName) {
    std::vector<ScaterringFunctionCoefficients> scatteringCoeffs;

    std::ifstream coeffsFile;
    coeffsFile.open(strFileName);
    if (!coeffsFile.is_open()) {
        itkExceptionMacro("Can't open dates file for reading!");
    }

    std::string line;
    int curLine = 0;
    while (std::getline(coeffsFile, line))
    {
        trim(line);
        if ((line.size() > 0) && (line[0] != '#') && (line[0] != '\r'))
        {
            ScaterringFunctionCoefficients coeffs;
            std::istringstream iss(line);
            float num; // The number in the line

            //while the iss is a number
            int i = 0;
            while ((iss >> num))
            {
                //look at the number
                switch(i) {
                case 0:
                    coeffs.V0 = num;
                    break;
                case 1:
                    coeffs.V1 = num;
                    break;
                case 2:
                    coeffs.R0 = num;
                    break;
                case 3:
                    coeffs.R1 = num;
                    break;
                default:
                    break;
                }
                i++;
            }
            if(i >= 4) {
                scatteringCoeffs.push_back(coeffs);
            } else {
                itkExceptionMacro("Invalid values line found at position " << curLine);
            }
        }
        curLine++;
    }

    return scatteringCoeffs;
}

std::string DirectionalCorrection::trim(std::string const& str)
{
    if(str.empty())
        return str;

    std::size_t firstScan = str.find_first_not_of(' ');
    std::size_t first     = firstScan == std::string::npos ? str.length() : firstScan;
    std::size_t last      = str.find_last_not_of(' ');
    return str.substr(first, last-first+1);
}


DirectionalCorrection::OutImageType::Pointer DirectionalCorrection::GetCorrectedImg()
{
    return m_DirectionalCorrectionFunctor->GetOutput();
}
