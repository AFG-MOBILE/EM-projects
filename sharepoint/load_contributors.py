from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.authentication_context import AuthenticationContext
import pandas as pd
from io import BytesIO

# Configurações de autenticação
site_url = 'https://credicorponline.sharepoint.com/:x:/r/sites/MejoraContinuaYAPE-EMs'
username = 'alexandrofrisone@yape.com.pe'
password = 'mkda2k@.RR'
relative_url = 'sites/MejoraContinuaYAPE-EMs/_layouts/15/Doc.aspx?sourcedoc=%7BC81B703D-C5B0-42D0-B316-8140A5B86F6A%7D&file=Base%20de%20Colaboradores%20_%20Gerencia%20de%20Tecnología%20Yape.xlsx'
https://credicorponline.sharepoint.com/:x:/s/MejoraContinuaYAPE-EMs/ET1wG8iwxdBCsxaBQKW4b2oB-nbV8rzAQvi7-Sdayeq_oA?e=6fo2Er
# Autenticação
ctx_auth = AuthenticationContext(site_url)
if ctx_auth.acquire_token_for_user(username, password):
    ctx = ClientContext(site_url, ctx_auth)
    web = ctx.web
    ctx.load(web)
    ctx.execute_query()

    # Acessando o arquivo no SharePoint
    response = File.open_binary(ctx, relative_url)
    bytes_file_obj = BytesIO()
    bytes_file_obj.write(response.content)
    bytes_file_obj.seek(0)

    # Carregando a planilha no pandas
    df = pd.read_excel(bytes_file_obj)
    print(df)
else:
    print(ctx_auth.get_last_error()) # type: ignore
