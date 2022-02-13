import pygsheets
import pandas as pd
import datetime

try:
	gc=pygsheets.authorize(service_file='spreadsheets-functions-5e4b27424a28.json')
except:
	comp_path="C:/Users/johnm/Documents/python/g_spreadsheets/"
	gc=pygsheets.authorize(service_file=comp_path+'spreadsheets-functions-5e4b27424a28.json')

def get_cotas_mes_max():
    if datetime.datetime.today().day <= 3: sub_m = 1
    else: sub_m = 0
    try:
        n = datetime.datetime.now()
        cotas_do_mes = pd.read_csv("http://dados.cvm.gov.br/dados/FI/DOC/INF_DIARIO/DADOS/inf_diario_fi_%d.csv"%(n.year*100+n.month-sub_m), sep=';')
    except:
        n = datetime.datetime.now()+datetime.timedelta(days=-15)
        cotas_do_mes = pd.read_csv("http://dados.cvm.gov.br/dados/FI/DOC/INF_DIARIO/DADOS/inf_diario_fi_%d.csv"%(n.year*100+n.month-sub_m), sep=';')
    cotas_do_mes_max = cotas_do_mes[cotas_do_mes.groupby(['CNPJ_FUNDO'])['DT_COMPTC'].transform(max) == cotas_do_mes['DT_COMPTC']]
    return cotas_do_mes_max

def atualiza_wallet(wallet_name,cotas_do_mes_max):
	sh = gc.open(wallet_name)
	wks = sh.worksheet('title','Fundos')

	fundos_disp = wks.get_as_df()
	cnpjs_disp = fundos_disp['CNPJ']

	idx_val = list(fundos_disp.columns).index('Valor Cota')
	idx_dt = list(fundos_disp.columns).index('Data Cota')
	cols_poss = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']

	dats = []
	vals = []
	for cnpj in cnpjs_disp:
		df_tmp = cotas_do_mes_max[cotas_do_mes_max['CNPJ_FUNDO']==cnpj].reset_index(drop=True)
		dats+=[[df_tmp.loc[0,'DT_COMPTC']]]
		vals+=[[df_tmp.loc[0,'VL_QUOTA']]] 
	wks.update_values("%s2:%s%d"%(cols_poss[idx_val],cols_poss[idx_val],1+len(cnpjs_disp)),
					vals
					)
	wks.update_values("%s2:%s%d"%(cols_poss[idx_dt],cols_poss[idx_dt],1+len(cnpjs_disp)),
					dats
					)
					
cotas_do_mes_max = get_cotas_mes_max()					
atualiza_wallet('Wallet',cotas_do_mes_max)
atualiza_wallet("Sofia's Wallet",cotas_do_mes_max)