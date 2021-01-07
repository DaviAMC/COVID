import codecs 
import numpy as np
import scipy.stats
import hashlib
import os
import painelCOVID_final as painel
from joblib import Parallel, delayed

date  = "20201222"   # data dos dados da análise 
date1 = "20201221"  # data dos dados da última análise 

gamma1 = 0.119 #limites considerados para o valor de gamma. o r0 vai ser estimado nesses limites
gamma2 = 0.182
alpha =  15

reglist = [["SP",""],["MG",""],["RJ",""],["BA",""],["PR",""],["RS",""],["PE",""],["CE",""],["PA",""],["SC",""],["MA",""],["GO",""],["AM",""],["ES",""],\
    ["PB",""],["RN",""],["MT",""],["AL",""],["PI",""],["DF",""],["MS",""],["SE",""],["RO",""],["TO",""],["AC",""],["AP",""],["RR",""]]

linecsv , dict_estados  = painel.read_github(date,reglist)

# Abertura do html base 
html_file = codecs.open(date+".html","w", encoding="iso-8859-1")

painel.write_opening(html_file,date,date1)

#esse bloco cuida da parte da criação de diretório
script_dir = os.path.dirname(__file__)
gifs = os.path.join(script_dir,'gifs/')
graf = os.path.join(script_dir,'graf/')
if not os.path.isdir(graf):
    os.makedirs(graf)
if not os.path.isdir(gifs):
    os.makedirs(gifs)
    
reg = ["Brasil",""]

R_smooth2 , dR_smooth2 = painel.graf_brasil(reg,linecsv,gamma1,gamma2,alpha,reglist,date,graf,gifs,dict_estados,html_file)

R_permil_global = []
D_permil_global = []
N_max = 0
R0list = np.zeros(len(reglist))

painel.write_js(html_file,R_permil_global,D_permil_global,reglist,R0list,N_max,date,linecsv,R_smooth2,dR_smooth2,gamma1,gamma2,alpha)     
              
if __name__ == "__main__":
    Parallel(n_jobs=27)(delayed(painel.graf)(reg,linecsv,gamma1,gamma2,alpha,reglist,date,graf,gifs,dict_estados) for reg in reglist)

html_file.write('<hr> \n')
html_file.write('<big><big><span style="font-weight: bold;">Estimativa de <i>r<sub>0</sub></i> para estados e algumas cidades - '+date[6:8]+"/"+date[4:6]+"/"+date[0:4]+'. Para saber mais sobre estas estimativas e como interpretá-las, veja <a href="covid.pdf">aqui</a>. Clique nos gráficos para mais detalhes.  </span></big></big><br> \n')
html_file.write('<br> \n')
html_file.write('<big><big><span style="font-weight: bold;"> Estados  </span></big></big><br> \n')

for reg in reglist:
    regfile = hashlib.md5(bytes(reg[0]+reg[1]+date,'utf-8')).hexdigest()  
    fig = '<img style="width: 216px; height: 144px;" src="'+regfile+'R0thumb.jpg">'
    html_file.write('<a href="'+regfile+'.html">'+fig+"</a> ")   

html_file.write('<br> \n')
html_file.write('<br> \n')

html_file.write('<big><big><span style="font-weight: bold;"> Cidades  </span></big></big><br> \n')

reglist = [["SP","São Paulo"],["SP","Campinas"],["SP","Guarulhos"],["SP","São Bernardo do Campo"],\
              ["SP","São José dos Campos"],["SP","Santo André"],["SP","Ribeirão Preto"],\
              ["SP","Osasco"],["SP","Sorocaba"], ["SP","Mauá"], ["SP","Santos"], ["SP","Diadema"],\
              ["SP","São Caetano do Sul"],["SP","Jundiaí"],["SP","Piracicaba"],\
              ["RJ","Rio de Janeiro"],["BA","Salvador"],["CE","Fortaleza"],["MG","Belo Horizonte"],\
              ["AM","Manaus"],["PR","Curitiba"], ["PE","Recife"], ["RS","Porto Alegre"], ["PA","Belém"],["GO","Goiânia"],\
              ["MA","São Luís"],["AL","Maceió"], ["PI","Teresina"],  ["RN","Natal"],\
              ["MS","Campo Grande"], ["PB","João Pessoa"],["PB","Campina Grande"],\
              ["SE","Aracaju"],["MT","Cuiabá"],["RO","Porto Velho"],["SC","Florianópolis"],\
              ["AP","Macapá"],["AC","Rio Branco"],["ES","Vitória"], ["RR","Boa Vista"],["TO","Palmas"]]

if __name__ == "__main__":
    Parallel(n_jobs=41)(delayed(painel.graf)(reg,linecsv,gamma1,gamma2,alpha,
    reglist,date,graf,gifs,dict_estados) for reg in reglist) 

for reg in reglist:
    regfile = hashlib.md5(bytes(reg[0]+reg[1]+date,'utf-8')).hexdigest()  
    fig = '<img style="width: 216px; height: 144px;" src="'+regfile+'R0thumb.jpg">'
    html_file.write('<a href="'+regfile+'.html">'+fig+"</a> ")       
       
html_file.close()


