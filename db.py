from sqlalchemy import create_engine
from bs4 import BeautifulSoup
import pandas as pd
import requests

def create_codePaysRegion_DataframeFromUrl(url):
  page = requests.get(url)
  soup = BeautifulSoup(page.content, 'html.parser')
  tables = soup.find_all('table')
  
  df = pd.DataFrame(columns=["Name", "Code"])
  for row in tables[0].find_all('tr')[2:]:
    row_data = row.find_all('td')
    individual_row = [data.text.strip() for data in row_data]
    if len(individual_row) > 3:
      individual_row = [individual_row[0], individual_row[3]]
      df.loc[len(df)] = individual_row
  return df

def create_approvedTrustList_DataframeFromUrl(url):
  page = requests.get(url)
  soup = BeautifulSoup(page.content, 'html.parser')
  tables = soup.find_all('table')
  df = pd.DataFrame(columns=[h.text.strip() for h in tables[0].find_all('th')])

  for i in range(len(tables)):
    for row in tables[i].find_all('tr')[1:]:
      row_data = row.find_all('td')
      individual_row = [data.text.strip() for data in row_data]
      df.loc[len(df)] = individual_row
  df = df.drop(df.columns[3:], axis=1)
  df.columns = ['codeCountryRegion', 'hLocation', 'cName']
  df.replace('', pd.NA, inplace=True)
  
  return df.dropna(how='all')

def createEngine(db_user, db_password, db_host, db_port, db_name):
  conn_str = f'postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
  return create_engine(conn_str)

def loadFromUrl(df, db_table):
  db_user = 'postgres'
  db_password = 'root'
  db_host = 'localhost'
  db_port = '5432'
  db_name = 'postgres'
  try:
    engine = createEngine(db_user, db_password, db_host, db_port, db_name)
    df.to_sql(db_table, engine, if_exists='fail')
    print('### Load ', db_table)
  except Exception as e:
    print('###' + str(e))

url = "https://helpx.adobe.com/acrobat/kb/approved-trust-list1.html"
db_table = 'approvedTrustList'

urlCode = "https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes#MYAN"
db_tableCode = 'codePaysRegion'

from sqlalchemy import create_engine
from bs4 import BeautifulSoup
import pandas as pd
import requests

def create_codePaysRegion_DataframeFromUrl(url):
  page = requests.get(url)
  soup = BeautifulSoup(page.content, 'html.parser')
  tables = soup.find_all('table')
  
  df = pd.DataFrame(columns=["Name", "Code"])
  for row in tables[0].find_all('tr')[2:]:
    row_data = row.find_all('td')
    individual_row = [data.text.strip() for data in row_data]
    if len(individual_row) > 3:
      individual_row = [individual_row[0], individual_row[3]]
      df.loc[len(df)] = individual_row
  return df

def create_approvedTrustList_DataframeFromUrl(url):
  page = requests.get(url)
  soup = BeautifulSoup(page.content, 'html.parser')
  tables = soup.find_all('table')
  df = pd.DataFrame(columns=[h.text.strip() for h in tables[0].find_all('th')])

  for i in range(len(tables)):
    for row in tables[i].find_all('tr')[1:]:
      row_data = row.find_all('td')
      individual_row = [data.text.strip() for data in row_data]
      df.loc[len(df)] = individual_row
  df = df.drop(df.columns[3:], axis=1)
  df.columns = ['codeCountryRegion', 'hLocation', 'cName']
  df.replace('', pd.NA, inplace=True)
  
  return df.dropna(how='all')

def createEngine(db_user, db_password, db_host, db_port, db_name):
  conn_str = f'postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
  return create_engine(conn_str)

def loadFromUrl(df, db_table):
  db_user = 'postgres'
  db_password = 'root'
  db_host = 'localhost'
  db_port = '5432'
  db_name = 'postgres'
  try:
    engine = createEngine(db_user, db_password, db_host, db_port, db_name)
    df.to_sql(db_table, engine, if_exists='fail')
    print('### Load ', db_table)
  except Exception as e:
    print('###' + str(e))

url = "https://helpx.adobe.com/acrobat/kb/approved-trust-list1.html"
db_table = 'approvedTrustList'

urlCode = "https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes#MYAN"
db_tableCode = 'codePaysRegion'
