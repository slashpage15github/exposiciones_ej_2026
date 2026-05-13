import kagglehub

# Download latest version
path = kagglehub.dataset_download("kindasomethin/drug-seizures-2019-2023")

# Region,SubRegion,Country,DrugGroup,DrugSubGroup,DrugName,Reference year,Kilograms,msCode columns

print("Path to dataset files:", path)