# Aim
To extract text from business card image(s). Store it in the MySQL local server. Display extracted data using pandas. 

## Data Collection
The data is collected from a [Google Drive source](https://drive.google.com/drive/folders/1FhLOdeeQ4Bfz48JAfHrU_VXvNTRgajhp) with five+ business card templates.

## Data Categorization
The textual data typically has information of the 
- <span style="color:#4b7bec">'Name of the business/person'</span>
- <span style="color:#fc5c65">'Designation'</span>
- <span style="color:#45aaf2">'Phone numbers'</span>
- <span style="color:#fed330">'Email Id'</span>
- <span style="color:#a55eea">'Website'</span>
- <span style="color:#1dd1a1">'Address'</span>
After the extraction, the UI has an option to either save or discard the same in MySQL database server.

## Supported Images
Current version of the BizCard reader is compatible with images of following extensions in formats:
- 'JPEG/JPG'.
- 'PNG'.

## Features
- Introduction (App characteristics)
- Extraction (Drive)
- Data Management: Migration of the extracted data to MySQL (SQL)
- Data Visualization (Plotly, pandas)

## Feedback
Please feel free to explore. Feedbacks are most welcome. For any comments or questions or queries, contact the UI developer [Vikas](mailto:vikki.4me@gmail.com). Thank you!
