import pandas as pd

#----------------------------------------------------------------
# Decided to create a separate module for the data loading and preparation part. 
# This helps with readibility and maintainability, and steps are easier to understand.
#----------------------------------------------------------------

class DataModel():
    """
    The DataModel class provides methods to load, prepare, and retrieve data obtained from github.
    """

    file_url = "https://raw.githubusercontent.com/drpawelo/data/main/health/OCED_simplified.csv"
    
    # Dictionary to shorten the originally very long column names.
    rename_dict = {
        "Cervical cancer screening, programme data_% of females aged 20-69 screened": "cervical_cancer_screening_%f2069",
        "Breast cancer screening, programme data_% of females aged 50-69 screened" : "breast_cancer_screening_%f5069",
        "Colorectal cancer screening, programme data_% of population aged 50-74 screened": "colorectal_cancer_screening_%5074",
        "Colorectal cancer screening, programme data_% of females aged 50-74 screened": "colorectal_cancer_screening_%f5074",
        "Colorectal cancer screening, programme data_% of males aged 50-74 screened": "colorectal_cancer_screening_%m5074",
        "Malignant neoplasm of colon, rectum and anus_Number": "colorectal_cancer_n",
        "Malignant neoplasm of colon, rectum and anus_Per 100 000 population": "colorectal_cancer_incidence",
        "Malignant neoplasm of trachea, bronchus and lung_Number": "lung_cancer_n",
        "Malignant neoplasm of trachea, bronchus and lung_Per 100 000 population": "lung_cancer_incidence",
        "Malignant neoplasm of skin_Number": "skin_cancer_n",
        "Malignant neoplasm of skin_Per 100 000 population": "skin_cancer_incidence",
        "Malignant neoplasm of breast_Number": "breast_cancer_n",
        "Malignant neoplasm of breast_Per 100 000 females": "breast_cancer_incidence_f",
        "Malignant neoplasm of uterus_Number": "uterine_cancer_n",
        "Malignant neoplasm of uterus_Per 100 000 females": "uterine_cancer_incidence_f",
        "Malignant neoplasm of ovary_Number": "ovarian_cancer_n",
        "Malignant neoplasm of ovary_Per 100 000 females": "ovarian_cancer_incidence_f",
        "Malignant neoplasm of prostate_Number": "prostate_cancer_n",
        "Malignant neoplasm of prostate_Per 100 000 males": "prostate_cancer_incidence_m",
        "Malignant neoplasm of bladder_Number": "bladder_cancer_n",
        "Malignant neoplasm of bladder_Per 100 000 population": "bladder_cancer_incidence",
        "Other Malignant neoplasms_Number": "other_cancer_n",
        "Other Malignant neoplasms_Per 100 000 population": "other_cancer_incidence"
    }
    
    def __init__(self) -> None:
        # reading data from url into csv.
        df = pd.read_csv(DataModel.file_url)

        # Reduce data to the subset needed in this use case.
        mask = ["year", "country"] + list(df.columns[(df.columns.str.contains('Malignant')) & 
                (df.columns.str.contains('Per 100 000') | df.columns.str.contains('Number')) | 
                (df.columns.str.contains('screening') & df.columns.str.contains('programme'))])
        
        # Storing the data in an attribute.
        self.data = df[mask]
    
    def clean_column_names(self) -> None:
        """
        Applying the clean column names from the dictionary to the dataset.
        """
        self.data = self.data.rename(columns= DataModel.rename_dict)
    
    def get_data(self) -> pd.DataFrame:
        """
        Cleans the column names and returns a dataframe that does not contain NaN values.
        Returns:
            _type_: pd.DataFrame
        """
        self.clean_column_names()
        self.data = self.data.fillna(0)
        return self.data
    
    def get_cancer_types(self) -> list[str]:
        """
        Creates a list of easy to read cancer types.
        Returns:
            _type_: list[str]
        """
        self.clean_column_names()
        cancer_types = []
        for column in self.data.columns[2:]:
            cancer_types.append(' '.join([word.capitalize() for word in column.split('_')[:2]]))
        cancer_types.remove("Cervical Cancer") # Only exists for screenings.
        return list(set(cancer_types))
    
    def get_units(self) -> list[str]:
        """
        Creates a list of easy to read units for filtering.
        Returns:
            _type_: list[str]
        """
        units = ["Total Number",
                    "Incidence per 100.000"]
        return sorted(units)
    
    def get_data_dictionary(self) -> dict:
        """
        Creates a dictionary with additional Information for certain cancer types that would otherwise be hidden from the user.
        Returns:
            _type_: dict
        """
        infos = {
            "Cervical Screening": "Cervical cancer screening is calculated as a % of women between 20 and 69 years old.",
            "Breast Screening": "Breast cancer screening is calculated as a % of women between 50 and 69 years old.",
            "Colorectal Screening": "Colorectal cancer screening is calculated as a % of man and women between 50 and 74 years old.",
            "Ovarian Cancer": "Reflects incidence per 100.000 women.",
            "Uterine Cancer": "Reflects incidence per 100.000 women.",
            "Breast Cancer": "Reflects incidence per 100.000 women.",
            "Prostate Cancer": "Reflects incidence per 100.000 man.",
        }
        return infos
    
    def get_screenings(self) -> list[str]:
        """
        Creates a list of easy to read screenings. For filtering purposes.
        Returns:
            _type_: list[str]
        """
        self.clean_column_names()
        columns = list(self.data.columns[self.data.columns.str.contains("screening")])
        screenings = []
        for words in columns:
            screenings.append(' '.join([word.capitalize() for word in words.split('_')[:2]]) + " Screening")
        return list(set(screenings))
    
    def get_years(self) -> list[int]:
        """
        Creates a list of years for filtering.
        Returns:
            _type_: list[int]
        """
        return list(sorted(set(self.data["year"])))
    
    def get_countries(self) -> list[str]:
        """
        Creates a list of countries for filtering.
        Returns:
            _type_: list[str]
        """
        return list(sorted(set(self.data["country"])))


    
class CountryModel():
    """
    This class contains centroid localization for countries.
    """
    
    file_url = r"https://raw.githubusercontent.com/DanielPiede/ShinyDashboard/main/raw/country_centroids.csv"
    
    def __init__(self) -> None:
        # Loarding the data on centroids from a csv in github.
        self.centroids = pd.read_csv(CountryModel.file_url).iloc[:,0:3]
    
    def get_centroid(self, country: str) -> tuple:
        # Get the position for a specific country (reversed order, to match latitude and longitude on maps.)
        pos = self.centroids[self.centroids["COUNTRY"] == country]
        return tuple(reversed(pos.values[0][:2]))