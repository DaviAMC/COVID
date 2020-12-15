#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 22 07:31:24 2020

@author: davi
"""
###TEM QUE FAZER AS MODIFICAÇÕES AINDA######
import codecs 
import numpy as np
import scipy.stats
import hashlib
import os
import painelCOVID_gif_v3 as painel
#import multiprocessing | usar essa biblioteca para adaptar para a quantidade de núcleos da máquina
from joblib import Parallel, delayed

date  = "20201018"   # data dos dados da análise 
date1 = "20201017"  # data dos dados da última análise 

gamma1 = 0.119 #limites considerados para o valor de gamma. o r0 vai ser estimado nesses limites
gamma2 = 0.182
alpha =  15

#num_cores = multiprocessing.cpu_count() | usar essa biblioteca para adaptar para a quantidade de núcleos da máquina

reglist = ["SP","MG","RJ","BA","PR","RS","PE","CE","PA","SC","MA","GO","AM","ES","PB","RN","MT","AL","PI","DF","MS","SE","RO","TO","AC","AP","RR"]
reglistcid = [["SP","São Paulo"],["SP","Campinas"],["SP","Guarulhos"],["SP","São Bernardo do Campo"],\
              ["SP","São José dos Campos"],["SP","Santo André"],["SP","Ribeirão Preto"],\
              ["SP","Osasco"],["SP","Sorocaba"], ["SP","Mauá"], ["SP","Santos"], ["SP","Diadema"],\
              ["SP","São Caetano do Sul"],["SP","Jundiaí"],["SP","Piracicaba"],\
              ["RJ","Rio de Janeiro"],["BA","Salvador"],["CE","Fortaleza"],["MG","Belo Horizonte"],\
              ["AM","Manaus"],["PR","Curitiba"], ["PE","Recife"], ["RS","Porto Alegre"], ["PA","Belém"],["GO","Goiânia"],\
              ["MA","São Luís"],["AL","Maceió"], ["PI","Teresina"],  ["RN","Natal"],\
              ["MS","Campo Grande"], ["PB","João Pessoa"],["PB","Campina Grande"],\
              ["SE","Aracaju"],["MT","Cuiabá"],["RO","Porto Velho"],["SC","Florianópolis"],\
              ["AP","Macapá"],["AC","Rio Branco"],["ES","Vitória"], ["RR","Boa Vista"],["TO","Palmas"]]
#
#
#   Leitura API brasil.io
# #
#linecsv , update_string , dict_estados  = painel.read_brasil_io(reglist, reglistcid)

#
#
#   Leitura API github (dados MS)
#
linecsv , update_string , dict_estados  = painel.read_github(date,reglist)
 

#
# Abertura do html base 
#
html_file = codecs.open(date+".html","w", encoding="iso-8859-1")




painel.write_opening(html_file,date,date1,update_string)


    
reg = ["Brasil",""]

res = painel.read_csv_data(reg,linecsv)

R_raw = res['R_raw'] #casos acumulados
D_raw = res['D_raw']#obitos acumulados
N_k = res['N_k']
First_Day = res['First_Day']
Last_Day = res['Last_Day']
Popul = res['Popul'] 



N_s = int(N_k/7)
N_d = N_k-7*N_s

dR_raw = np.zeros(N_k)#casos novos
for i in range (1,N_k):
    dR_raw[i] = R_raw[i] - R_raw[i-1]
    
dD_raw = np.zeros(N_k)
for i in range (1, N_k):
    dD_raw[i] = D_raw[i] - D_raw[i-1]     

#
# Suavização: 2 iterações da média móvel   
#
R_smooth2 = painel.smooth(R_raw,3,2)

#
# Suavização: 4 iterações da média móvel   
#
R_smooth4 = painel.smooth(R_raw,3,4)


D_smooth4 = painel.smooth(D_raw,3,4)


dR_smooth2 = np.zeros(N_k)#diferenças do smooth2
for i in range (1,N_k):
    dR_smooth2[i] = R_smooth2[i] - R_smooth2[i-1]
    
dR_smooth4 = np.zeros(N_k)#diferenças do smooth4
for i in range (1,N_k):
    dR_smooth4[i] = R_smooth4[i] - R_smooth4[i-1]
    
d2R_smooth4 = np.zeros(N_k)#diferenças do drsmooth4
for i in range (1,N_k):
    d2R_smooth4[i] = dR_smooth4[i] - dR_smooth4[i-1]
    
dD_smooth4 = np.zeros(N_k)
for i in range(1,N_k):
    dD_smooth4[i] = D_smooth4[i] - D_smooth4[i-1]
    
R_prev = np.zeros(5)
T_prev = np.zeros(5)
a,b,r_value, p_value, std_err =  scipy.stats.linregress(np.linspace(-9,0,10),R_raw[N_k-10:N_k])#faz a regressão linear, com os R_raw no eixo y
for j in range (0,5):
    T_prev[j] = N_k+j
    R_prev[j] = a*(j+1) + R_raw[N_k-1]

R0_est_dif_0 , R0_est_dif_1 = painel.R0dif(R_smooth4,dR_smooth4,d2R_smooth4,Popul,gamma1,gamma2,alpha)#limites do valor de r0 no método diferencial
R0_est_int_0 , R0_est_int_1 = painel.R0int(R_smooth2,dR_smooth2,Popul,gamma1,gamma2,alpha)#limites do valor de r0 no método integral

r_avg = np.mean(np.concatenate( (R0_est_int_0[N_k-17:N_k-3] , R0_est_int_1[N_k-17:N_k-3] ) ) )
std_err = np.std(np.concatenate( (R0_est_int_0[N_k-17:N_k-3] , R0_est_int_1[N_k-17:N_k-3])  ) )

print(r_avg)
   
R01 = min(R0_est_int_0[N_k-4],R0_est_int_1[N_k-4])
R02 = max(R0_est_int_0[N_k-4],R0_est_int_1[N_k-4])
    
nR = 1 - 1/r_avg 

regfile = hashlib.md5(bytes(reg[0]+reg[1]+date,'utf-8')).hexdigest()#cria um arquivo com o nome da cidade e data e associa a um hash  

if reg[1] == "":
    regstr = reg[0]#nome da região que a gente tá trabalhando
else:
    regstr = reg[1]+' - '+reg[0]
    
#esse bloco cuida da parte da criação de diretório
script_dir = os.path.dirname(__file__)
gifs = os.path.join(script_dir,'gifs/')
graf = os.path.join(script_dir,'graf/')
if not os.path.isdir(graf):
    os.makedirs(graf)
if not os.path.isdir(gifs):
    os.makedirs(gifs)

painel.drawCA(R_raw,R_smooth4,regstr,regfile,date)#cria gráfico de casos acumulado e salva um .jpg na própria pasta desse documento
painel.drawMA(D_raw,D_smooth4,regstr,regfile,date)
painel.drawNC(dR_raw,dR_smooth4,regstr,regfile,date,graf,gifs)
painel.drawPM(R_raw,D_raw,Popul,regstr,regfile,date) 
painel.drawR0dif(R0_est_dif_0,R0_est_dif_1,regstr,regfile,date)
painel.drawR0int(R0_est_int_0,R0_est_int_1,regstr,regfile,date)
painel.drawMU(R_smooth4,dR_smooth4,Popul,gamma1,gamma2,alpha,regstr,regfile,date)
painel.drawCAS(R_raw,D_raw,N_s,N_d,regstr,regfile,date)
painel.drawNM(dD_raw,dD_smooth4,regstr,regfile,date)
painel.drawNM_NC(dR_raw,dD_raw,regstr,regfile,date)
     
write_dict = { \
     'html_file'  : html_file  , \
            'reg' :  regstr ,\
        'regfile' :  regfile ,\
            'date': date , \
            'res' :  res , \
            'N_s' : N_s ,\
            'N_d' : N_d ,\
          'r_avg' :  r_avg,\
        'std_err' : std_err ,\
           'R01'  : R01 , \
            'R02' : R02 ,\
            'nR'  :  nR , \
        'R_prev'  :  R_prev  }                  
    
update_date = ""
    
painel.write_analise(write_dict,update_date,gifs)

html_file_local = codecs.open(regfile+".html","w", encoding="iso-8859-1")

write_dict['html_file'] = html_file_local

painel.write_analise(write_dict,update_date,gifs)

html_file_local.close()

wkhtmltopdf = "wkhtmltopdf --quiet "+regfile+".html "+regfile+".pdf"#converte o html em pdf
    
os.system(wkhtmltopdf)
 
#até aqui foi Brasil

reglist1 = ["SP","MG","RJ","BA","PR","RS","PE","CE","PA","SC","MA","GO","AM","ES","PB","RN","MT","AL","PI","DF","MS","SE","RO","TO","AC","AP","RR"]
reglist = [["SP",""],["MG",""],["RJ",""],["BA",""],["PR",""],["RS",""],["PE",""],["CE",""],["PA",""],["SC",""],["MA",""],["GO",""],["AM",""],["ES",""],\
    ["PB",""],["RN",""],["MT",""],["AL",""],["PI",""],["DF",""],["MS",""],["SE",""],["RO",""],["TO",""],["AC",""],["AP",""],["RR",""]]

R_permil_global = []
D_permil_global = []
N_max = 0
R0list = np.zeros(len(reglist))

for reg in reglist:
    print(reg)
    res = painel.read_csv_data(reg,linecsv)
    R_raw = res['R_raw'] 
    D_raw = res['D_raw']
    Popul = res['Popul']
    N_k = res['N_k']
    R_permil_global.append(1.0e6*R_raw/Popul)
    D_permil_global.append(1.0e6*D_raw/Popul)    
    if N_k>N_max:
        N_max = N_k

if __name__ == "__main__":
    Parallel(n_jobs=27)(delayed(painel.graf_estado)(reg,linecsv,N_max,R_permil_global,D_permil_global,
                gamma1,gamma2,alpha,R0list,reglist,date,graf,gifs,
                dict_estados) for reg in reglist)

painel.write_js(html_file,R_permil_global,D_permil_global,reglist1,R0list,N_max,date)    

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
    Parallel(n_jobs=41)(delayed(painel.graf_cidade)(reg,linecsv,N_max,R_permil_global,D_permil_global, 
                gamma1,gamma2,alpha,R0list,reglist,date,graf,gifs,
                dict_estados) for reg in reglist) #observar essa questão do dict_estados

for reg in reglist:
    regfile = hashlib.md5(bytes(reg[0]+reg[1]+date,'utf-8')).hexdigest()  
    fig = '<img style="width: 216px; height: 144px;" src="'+regfile+'R0thumb.jpg">'
    html_file.write('<a href="'+regfile+'.html">'+fig+"</a> ")       
       
html_file.close()


