copy C:\Temp\Charts\Covid19_Cases_files\image001.png C:\Temp\LogCases.png
copy C:\Temp\Charts\Covid19_Cases_files\image002.png C:\Temp\CovidCases.png
copy C:\Temp\Charts\Covid19_Cases_files\image003.png C:\Temp\NewCases.png
copy C:\Temp\Charts\Covid19_Cases_files\image004.png C:\Temp\LogDeaths.png
copy C:\Temp\Charts\Covid19_Cases_files\image005.png C:\Temp\CovidDeaths.png
copy C:\Temp\Charts\Covid19_Cases_files\image006.png C:\Temp\NewDeaths.png
pscp -P 4830 C:\Temp\*.png keithbarr@droplet1.colorado-barrs.com:/home/keithbarr/public_html/covid19/index_files