import numpy as np
import matplotlib.pyplot as plt
import requests
import csv
from datetime import datetime
import time 
import io
import zipfile
import scipy.stats
import imageio
import os
import hashlib
import codecs



def read_github(date,reglist):

    git_url = 'https://raw.githubusercontent.com/albertosaa/COVID/master/data/'+date+'.csv.zip'
    r = requests.get(git_url)
    zip_file = zipfile.ZipFile(io.BytesIO(r.content))
    files = zip_file.namelist()
    with zip_file.open(files[0], 'r') as csvfile_byte:
        with io.TextIOWrapper(csvfile_byte) as csv_file:
            cr = csv.reader(csv_file,delimiter=';')
            linecsv = list(cr)

    dict_estados = {}
    for reg in reglist:  
        dict_estados.update({ reg[0] : ""})
        
        
    return linecsv , dict_estados

def read_csv_data(reg,linecsv):
#
#    
# Lê o arquivo CSV e retorna a série temporal para os casos acumulados, número de elementos na série,
#  série de óbitos, datas do primeiro e últimos casos e população
#
#
    Y = []
    YD = []
    k = 0 
    
    if reg[0] == "Brasil":
        for row in linecsv:
            if (row[0] == reg[0]) :
                if k == 0:
                    First_Day = row[7]
                    Pop = int(row[9])
                    
                Y.append(int(row[10]))
                YD.append(int(row[12]))
                
                k += 1
                Last_Day = row[7]
 
    elif  reg[1] == "":    
        for row in linecsv:
            if (row[1] == reg[0]) and (row[2] == "") and ( row[9] != "" ):
                if k == 0:
                    First_Day = row[7]
                    Pop = int(row[9])
                    
                Y.append(int(row[10]))
                YD.append(int(row[12]))

                k += 1
                Last_Day = row[7]
 
    else:
        for row in linecsv:
            if (row[1] == reg[0]) and (row[2] == reg[1]):
                if k == 0:
                    First_Day = row[7]
                    Pop = int(row[9])
                    
                Y.append(int(row[10]))
                YD.append(int(row[12]))

                k += 1
            Last_Day = row[7]
  
    dict_return = {'R_raw' : np.array(Y), \
                   'D_raw' :np.array(YD), \
                    'N_k' : k, \
                 'First_Day' : First_Day,\
                 'Last_Day'  : Last_Day, \
                   'Popul' : Pop   }
    
    return dict_return


def write_opening(html_file,date,date1):
     
    html_file.write('<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd"> \n')
    html_file.write('<html><head> \n')
    html_file.write('<link rel="icon" type="image/x-icon"  href="favicon.ico">  \n')
    html_file.write('<meta content="text/html; charset=ISO-8859-1" http-equiv="content-type"><title>Painel Coronavirus</title><meta http-equiv="content-type" content="text/html; charset=utf-8"></head><body> \n')
    html_file.write('<div style="text-align: center;"><big><big><big><span style="font-weight: bold;">Painel Coronavírus</span></big></big></big><br> \n')
    html_file.write(date[6:8]+"/"+date[4:6]+"/"+date[0:4] + "<br></div> \n")
    html_file.write('<br> \n')
    html_file.write('<br> \n')
    html_file.write('<div style="text-align: center;">  <big> <big> Alberto Saa </big> </big> <br></div> \n')
    html_file.write('<div style="text-align: center;"> <big> <big> UNICAMP </big> </big></div> \n')
    html_file.write('<br> \n')
    html_file.write('<br> \n')
    html_file.write('<br>Esta página apresenta uma análise automática dos casos de COVID-19 a partir de dados públicos. (Clique <a href="dadosCOVID.html">aqui</a> para saber mais sobre a importação destes dados). Todos os detalhes técnicos sobre a análise estão <a href="covid.pdf">aqui</a>. A análise do dia anterior está <a href="'+date1+'.html">aqui</a>.') 
    html_file.write('O objetivo deste sistema é puramente educacional, com foco na análise de dados e programação em Python, e não em epidemiologia. Não obstante, todos os dados tratados aqui são reais e, portanto, os resultados talvez possam ter alguma relevância para se entender a dinâmica real da epidemia de COVID-19, a qual está muito bem analisada, por exemplo, <a href="https://covid19br.github.io/">aqui</a>.  ')
    html_file.write('Os dados e códigos necessários para gerar esta página estão <a href="https://github.com/albertosaa/COVID">aqui</a>, sinta-se à vontade para utilizá-los como quiser. <br> \n')
    html_file.write('<br> \n')
    html_file.write('Análise realizada a partir dos dados do Ministério da Saúde, clique <a href="dadosCOVID.html">aqui</a> para mais detalhes. <br> \n')
    html_file.write('<br> \n')
    html_file.write('<hr> \n')

    
    return 

def write_analise(write_dict,update_date,gifs):
    
    
    html_file = write_dict['html_file']
    reg = write_dict['reg']
    regfile = write_dict['regfile']
    date = write_dict['date']
    
    R_raw = write_dict['res']['R_raw']
    D_raw = write_dict['res']['D_raw'] 
    N_k = write_dict['res']['N_k']
    First_Day = write_dict['res']['First_Day']
    Last_Day = write_dict['res']['Last_Day']
    Popul = write_dict['res']['Popul'] 
  
    N_s = write_dict['N_s']
    N_d = write_dict['N_d']
    
    r_avg = write_dict['r_avg']
    std_err = write_dict['std_err']
    
    R01 = write_dict['R01']
    R02 = write_dict['R02']
    nR = write_dict['nR']
    R_prev = write_dict['R_prev']
    

    html_file.write('<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd"> \n')
    html_file.write('<html><head> \n')
    html_file.write('<link rel="icon" type="image/x-icon"  href="favicon.ico">  \n')
    html_file.write('<meta content="text/html; charset=ISO-8859-1" http-equiv="content-type"><title>Painel Coronavirus</title><meta http-equiv="content-type" content="text/html; charset=utf-8"></head><body> \n')
    html_file.write('<big><big><span style="font-weight: bold;"> '+reg+' - '+date[6:8]+"/"+date[4:6]+"/"+date[0:4]+'. </span></big></big> <br> \n')    
    html_file.write('Detalhes técnicos, <a href="covid.pdf">aqui</a>. Clique <a href='+regfile+'.pdf>aqui</a> para uma versão em PDF desta análise. \n')

    html_file.write('<br> \n')
    html_file.write('<br> \n')

    html_file.write('População: '+format(Popul,",d").replace(",", ".")+'.   \n')

    if N_d == 0:    
        html_file.write('Início e fim da série: '+First_Day+' e '+Last_Day+'. ('+str(N_k)+' elementos - '+str(N_s)+' semanas). <br> \n')
    elif N_d == 1:
        html_file.write('Início e fim da série: '+First_Day+' e '+Last_Day+'. ('+str(N_k)+' elementos - '+str(N_s)+' semanas e '+str(N_d)+' dia). <br> \n')
    else:
        html_file.write('Início e fim da série: '+First_Day+' e '+Last_Day+'. ('+str(N_k)+' elementos - '+str(N_s)+' semanas e '+str(N_d)+' dias). <br> \n')
        
    if update_date != "":
        html_file.write('Última atualização na plataforma <a href="https://brasil.io/dataset/covid19/caso_full/">brasil.io</a>: '+update_date+'. <br> \n')
        
    html_file.write('Número de casos totais e mortes: '+format(R_raw[N_k-1],",d").replace(",", ".")+' e '+format(D_raw[N_k-1],",d").replace(",", ".")+'. ('+format(int(round(1e6*R_raw[N_k-1]/Popul)),",d").replace(",", ".")+' e '+format(int(round(1e6*D_raw[N_k-1]/Popul)),",d").replace(",", ".") + ' por milhão de habitantes, respectivamente.) <br> \n')
    html_file.write('<i>r<sub>0</sub></i> (integral) efetivo médio (duas últimas semanas - três dias de atraso): '+'{0:.2f}'.format(r_avg).replace(".",",")+' (std = '+'{0:.2f}'.format(std_err).replace(".",",")+').  \n')                      
    html_file.write('Último intervalo para  <i>r<sub>0</sub></i> (três dias de atraso): ('+'{0:.2f}'.format(R01).replace(".",",")+' : '+'{0:.2f}'.format(R02).replace(".",",")+'). <br> \n')                      
    
    html_file.write('Limiar imunidade de grupo  <i>n<sub>R</sub> </i> (baseado no valor de <i>r<sub>0</sub></i> (integral) efetivo médio) = '+'{0:.2f}'.format(nR).replace(".",",")+".  <br> \n")
    
    prevstr = ""
    for i in range (0,4):
        prevstr = prevstr+format(int(R_prev[i]),",d").replace(",", ".")+', '    
    prevstr = prevstr+format(int(R_prev[4]),",d").replace(",", ".")+"."
    
    html_file.write('Previsão do número total de casos para os próximos 5 dias: '+prevstr+' <br> \n')

    html_file.write('<br> \n')
    html_file.write('<div style="text-align: center;"><img style="width: 432px; height: 288px;" alt="Casos Acumulados" src="'+gifs+regfile+"CA.gif"+'">&nbsp; <img style="width: 432px; height: 288px;" alt="Mortes Acumuladas" src="'+gifs+regfile+"MA.gif"+'"><br></div>')
    html_file.write('<div style="text-align: center;"><img style="width: 432px; height: 288px;" alt="Novos casos" src="'+gifs+regfile+"NC.gif"+'">&nbsp; <img style="width: 432px; height: 288px;" alt="Novas mortes" src="'+gifs+regfile+"NM.gif"+'"><br></div>')
    html_file.write('<div style="text-align: center;"><img style="width: 432px; height: 288px;" alt="Casos por semana" src="'+gifs+regfile+"CAS.gif"+'">&nbsp; <img style="width: 432px; height: 288px;" alt="Mortes por semana" src="'+gifs+regfile+"MS.gif"+'"><br></div>')
    html_file.write('<div style="text-align: center;"><img style="width: 432px; height: 288px;" alt="Casos e mortes por milhao" src="'+regfile+"pm.jpg"+'">&nbsp; <img style="width: 432px; height: 288px;" alt="Razão entre novas mortes e novos casos" src="'+regfile+"NM_NC.jpg"+'"><br></div>')    
    html_file.write('<div style="text-align: center;"><img style="width: 432px; height: 288px;" alt="r0 - dif" src="'+regfile+"R0dif.jpg"+'">&nbsp; <img style="width: 432px; height: 288px;" alt="R) - int" src="'+regfile+"R0int.jpg"+'"><br></div>')
    html_file.write('<div style="text-align: center;"><img style="width: 432px; height: 288px;" alt="mu" src="'+regfile+"mu.jpg"+'"><br></div>')###
    html_file.write('<br> \n')
    html_file.write('<br> \n')
    

    
    return


def movavg(Y,n):
#
#
# Retorna j iteraçõs da média móvel com janela (2n+1), com as bordas tratadas como descrito no texto
#
#    
    k = Y.size
    Y_smooth = np.zeros(k)
    
    Y_edge = np.concatenate( ( Y[0]*np.ones(n) , Y , Y[ k-n : k] + Y[k-1] - Y[k-n-1] )  )
    
    for i in range (0,k):
        Y_smooth[i]  =  np.sum(Y_edge[i:i+2*n+1])/(2*n+1)
        
    return Y_smooth

def smooth(Y,n,j):
#
#
# Retorna j iteraçõs da média móvel com janela (2n+1), com as bordas tratadas como descrito no texto
#
#    
    k = Y.size

    R_smooth = np.zeros(k)
    
    R_smooth = movavg(Y,n)
    for i in range (0,j):
        R_smooth = movavg(R_smooth,3)
        
    return R_smooth

def R0dif(R_smooth,dR_smooth,d2R_smooth,Popul,gamma1,gamma2,alpha):
# Retorna o valor de R0, calculado nos limites extremos de gamma
    
    M1 =  d2R_smooth + gamma1*dR_smooth 
    G1 = gamma1*dR_smooth -  alpha*(dR_smooth**2 + gamma1*dR_smooth*R_smooth)/Popul 
    
    M2 =  d2R_smooth + gamma2*dR_smooth 
    G2 = gamma2*dR_smooth -  alpha*(dR_smooth**2 + gamma2*dR_smooth*R_smooth)/Popul 
    
    return  M1/G1 ,  M2/G2

def R0int(R_smooth,dR_smooth,Popul,gamma1,gamma2,alpha):
# Retorna o valor de R0, calculado nos limites extremos de gamma
#            Calculo alternativo
    Nk = R_smooth.size 
    R01 = np.zeros(Nk)
    R02 = np.zeros(Nk)
    X = np.zeros(7)
    Y = np.zeros(7)
    
    for i in range (3,Nk-3):
        
        Y = np.log((Popul - alpha*dR_smooth[i-3:i+4]/gamma1 - alpha*R_smooth[i-3:i+4])/(Popul - alpha*dR_smooth[i-3]/gamma1 - alpha*R_smooth[i-3]))
        X = alpha*(R_smooth[i-3:i+4] - R_smooth[i-3])/Popul
           
        R01[i],b,r_value, p_value, std_err =  scipy.stats.linregress(X,Y)
        
        Y = np.log((Popul - alpha*dR_smooth[i-3:i+4]/gamma2 - alpha*R_smooth[i-3:i+4])/(Popul - alpha*dR_smooth[i-3]/gamma2 - alpha*R_smooth[i-3]))

        R02[i],b,r_value, p_value, std_err =  scipy.stats.linregress(X,Y)
        
    return  -R01 ,  -R02

def drawCA(R_raw,R_smooth,reg,regfile,date,graf,gifs):
#
# Gráfico Casos acumulados#
    image = []
    N_k = R_raw.size
    for i in range(10, N_k+1):
        plt.grid(False)
        plt.ylim(0,np.amax(R_raw))
        R_smooth_i = R_smooth[:i]
        R_raw_i = R_raw[:i]
        plt.plot(np.linspace(0,i-1,i),R_smooth_i,"r")
        plt.bar(np.linspace(0,i-1,i),R_raw_i)
        plt.xlabel("Dias")
        plt.ylabel("Casos")
        plt.title("Casos acumulados - "+reg+" - "+date[6:8]+"/"+date[4:6]+"/"+date[0:4])
        plt.savefig(graf+regfile+"CA.jpg",bbox_inches="tight")
        plt.close()
        image.append(imageio.imread(graf+regfile+"CA.jpg"))
    imageio.mimsave(gifs+regfile+"CA.gif",image, loop = 1)

def drawMA(D_raw,D_smooth,reg,regfile,date,graf,gifs):

#Gráfico óbitos acumulados
    image = []
    N_k = D_raw.size
    for i in range(10, N_k+1):
        plt.grid(False)
        plt.ylim(0,np.amax(D_raw))
        D_smooth_i = D_smooth[:i]
        D_raw_i = D_raw[:i]
        plt.plot(np.linspace(0,i-1,i),D_smooth_i,"r")
        plt.bar(np.linspace(0,i-1,i),D_raw_i)
        plt.xlabel("Dias")
        plt.ylabel("Mortes")
        plt.title("Mortes acumuladas - "+reg+" - "+date[6:8]+"/"+date[4:6]+"/"+date[0:4])
        plt.savefig(graf+regfile+"MA.jpg",bbox_inches="tight")
        plt.close()
        image.append(imageio.imread(graf+regfile+"MA.jpg"))
    imageio.mimsave(gifs+regfile+"MA.gif",image, loop = 1)    
    return


def drawNC(dR_raw,dR_smooth,reg,regfile,date,graf,gifs):
#
# Gráfico Novos Casos  
#
    image = []
    N_k = dR_raw.size
    for i in range(10, N_k+1):
        plt.grid(False)
        plt.ylim(0,np.amax(dR_raw))
        dR_smooth_i = dR_smooth[:i]
        dR_raw_i = dR_raw[:i]
        plt.plot(np.linspace(0,i-1,i),dR_smooth_i,"r")
        plt.bar(np.linspace(0,i-1,i),dR_raw_i)
        plt.xlabel("Dias")
        plt.ylabel("Casos")
        plt.title("Novos casos - "+reg+" - "+date[6:8]+"/"+date[4:6]+"/"+date[0:4])
        plt.savefig(graf+regfile+"NC.jpg",bbox_inches="tight")
        plt.close()
        image.append(imageio.imread(graf+regfile+"NC.jpg"))
    imageio.mimsave(gifs+regfile+"NC.gif",image, loop = 1)#first argument is export name, and second is the list with the frames
    
    return

def drawNM(dD_raw,dD_smooth,reg,regfile,date,graf,gifs):
    
    N_k = dD_raw.size
    image = []    
    for i in range(10, N_k+1):
        plt.grid(False)
        plt.ylim(0,np.amax(dD_raw))
        dD_smooth_i = dD_smooth[:i]
        dD_raw_i = dD_raw[:i]
        plt.plot(np.linspace(0,i-1,i),dD_smooth_i,"r")
        plt.bar(np.linspace(0,i-1,i),dD_raw_i)
        plt.xlabel("Dias")
        plt.ylabel("Mortes")
        plt.title("Novas mortes - "+reg+" - "+date[6:8]+"/"+date[4:6]+"/"+date[0:4])
        plt.savefig(graf+regfile+"NM.jpg",bbox_inches="tight")
        plt.close()
        image.append(imageio.imread(graf+regfile+"NM.jpg"))
    imageio.mimsave(gifs+regfile+"NM.gif",image, loop = 1)
    return

def drawNM_NC(dR_raw,dD_raw,reg,regfile,date):
    
    N_k = dD_raw.size
    NC = np.array(dR_raw)
    NM = np.array(dD_raw)
    y = NM/NC
    y_smooth = smooth(y,3,2)
    plt.grid(False)
    plt.plot(np.linspace(0, N_k-1, N_k),y, 'o', color='blue')
    plt.plot(np.linspace(0, N_k-1, N_k),y_smooth, color='red')
    plt.xlabel("Dias")
    plt.ylabel("Novas mortes / Novos casos")
    plt.title("Razão entre novas mortes e novos casos - "+reg+" - "+date[6:8]+"/"+date[4:6]+"/"+date[0:4])
    plt.savefig(regfile+"NM_NC.jpg",bbox_inches="tight") 

    plt.close()
        
    return 

def drawPM(R_raw,D_raw,Popul,reg,regfile,date):
    
    N_k = R_raw.size
    
    fig, ax1 = plt.subplots()
    
    ax2 = ax1.twinx()
    
    ax1.plot(np.linspace(0,N_k-1,N_k),1.0e6*R_raw/Popul,linewidth=4,color='b')
    ax2.plot(np.linspace(0,N_k-1,N_k),1.0e6*D_raw/Popul,linewidth=4,color='r')    
    
    ax1.set_yscale("log")
    ax2.set_yscale("log")
    
    ax1.set_xlabel('Dias')
    ax1.set_ylabel('Casos por milhão', color = 'b')
    ax2.set_ylabel('Mortes por milhão', color='r' )
    plt.title("Casos e mortes por milhão - "+reg+" - "+date[6:8]+"/"+date[4:6]+"/"+date[0:4])
    plt.savefig(regfile+"pm.jpg",bbox_inches="tight") 

    plt.close()
        
    return

def drawR0dif(R0_est_0,R0_est_1,reg,regfile,date):
#
# Gráfico r0 efetivo
#     
    N_k = R0_est_0.size
    T = np.linspace(0,N_k-1,N_k)
    
    plt.grid(True)    
    plt.fill_between(T[N_k-5:],np.zeros(5),4*np.ones(5), color = "bisque")
    plt.plot(T[3:],np.ones(N_k-3),"c",linewidth=4)
    plt.plot(T[3:] , R0_est_0[3:],"r--")
    plt.plot(T[3:] , R0_est_1[3:], "r--")
    plt.fill_between(T[3:] , R0_est_0[3:], R0_est_1[3:] , color = "lightcoral")
    plt.ylim(0,4)
    plt.xlabel("Dias")
    plt.ylabel("$r_0$")
    plt.title("$r_0$ efetivo (dif) - "+reg+" - "+date[6:8]+"/"+date[4:6]+"/"+date[0:4])
    plt.savefig(regfile+"R0dif.jpg",bbox_inches="tight") 
 
    plt.close()
    
    return

def drawR0int(R0_est_0,R0_est_1,reg,regfile,date):
#
# Gráfico r0 efetivo
#     
    N_k = R0_est_0.size
    T = np.linspace(0,N_k-1,N_k)
    
    plt.grid(True)    
    plt.fill_between(T[N_k-5:],np.zeros(5),4*np.ones(5), color = "bisque")
    plt.plot(T[3:],np.ones(N_k-3),"c",linewidth=4)
    plt.plot(T[3:N_k-3] , R0_est_0[3:N_k-3],"r--")
    plt.plot(T[3:N_k-3] , R0_est_1[3:N_k-3], "r--")
    plt.fill_between(T[3:N_k-3] , R0_est_0[3:N_k-3], R0_est_1[3:N_k-3] , color = "lightcoral")
    plt.ylim(0,4)
    plt.xlabel("Dias")
    plt.ylabel("$r_0$")
    plt.title("$r_0$ efetivo (int) - "+reg+" - "+date[6:8]+"/"+date[4:6]+"/"+date[0:4])
    plt.savefig(regfile+"R0int.jpg",bbox_inches="tight") 
 
    plt.close()
    
    return
    
def drawR0thumb(R0_est_0,R0_est_1,reg,regfile,date):
    
    N_k = R0_est_0.size
    T = np.linspace(0,N_k-1,N_k)
        
    plt.figure(figsize=(4,2.2))
    plt.grid(True)  
    plt.fill_between(T[N_k-5:],np.zeros(5),4*np.ones(5), color = "bisque")
    plt.plot(T[3:],np.ones(N_k-3),"c",linewidth=4)
    plt.plot(T[3:N_k-3] , R0_est_0[3:N_k-3],"r--")
    plt.plot(T[3:N_k-3] , R0_est_1[3:N_k-3], "r--")  
    plt.fill_between(T[3:N_k-3] , R0_est_0[3:N_k-3], R0_est_1[3:N_k-3] , color = "lightcoral")
    plt.ylim(0.5,2.5)
    plt.title(reg,fontsize=18)
    plt.savefig(regfile+"R0thumb.jpg",bbox_inches="tight") 

    plt.close()
                 
    
    return
 
   

def drawMU(R_smooth,dR_smooth,Popul,gamma1,gamma2,alpha,reg,regfile,date):
#
# Gráfico mu 
#      
    N_k = R_smooth.size
    T = np.linspace(0,N_k-1,N_k)

    mu_0 = alpha*(dR_smooth + gamma1*R_smooth)/(Popul*gamma1)
    mu_1 = alpha*(dR_smooth + gamma2*R_smooth)/(Popul*gamma2)
    
    mu_max = max(np.max(mu_0),np.max(mu_1))
    
    plt.grid(True)    
    plt.fill_between(T[N_k-5:],np.zeros(5),mu_max*np.ones(5), color = "bisque")
    plt.plot(T[3:] , mu_0[3:],"r--")
    plt.plot(T[3:] , mu_1[3:], "r--")
    plt.fill_between(T[3:] , mu_0[3:], mu_1[3:] , color = "lightcoral")
    plt.xlabel("Dias")
    plt.ylabel("μ")
    plt.title("Razão μ - "+reg+" - "+date[6:8]+"/"+date[4:6]+"/"+date[0:4]+" (α = "+'{0:.1f}'.format(alpha).replace(".",",")+")")
    plt.savefig(regfile+"mu.jpg",bbox_inches="tight") 
 
    plt.close()
    
    return

def drawCAS(R_raw,D_raw,N_s,N_d,reg,regfile,date,graf,gifs):
    
    N_k = R_raw.size
    
    if N_d == 0:
        R_week = np.zeros(N_s)
        D_week = np.zeros(N_s)
        T_week = np.linspace(0,N_s-1,N_s)
    else:
        R_week = np.zeros(N_s)
        D_week = np.zeros(N_s)
        T_week = np.linspace(0,N_s,N_s+1)
        
    R_week[0] = R_raw[6]
    D_week[0] = D_raw[6]

    for i in range (1,N_s):
        R_week[i] = R_raw[7*(i+1)-1] - R_raw[7*i-1]       
        D_week[i] = D_raw[7*(i+1)-1] - D_raw[7*i-1]    
        
    R_week_rem = R_raw[N_k-1] - R_raw[7*N_s-1]   
    D_week_rem = D_raw[N_k-1] - D_raw[7*N_s-1]  

    if N_d == 0:
        # Novos casos por semana
        #
        image = []
        for i in range(0, N_s):         
            plt.grid(False)
            plt.ylim(0,np.amax(R_week))
            T_week_i = T_week[:i]
            R_week_i = R_week[:i]            
            plt.bar(T_week_i,R_week_i)
            plt.xlabel("Semanas desde o primeiro caso")
            plt.ylabel("Casos")
            plt.title("Casos por semana - "+reg+" - "+date[6:8]+"/"+date[4:6]+"/"+date[0:4])
            plt.savefig(graf+regfile+"CAS.jpg",bbox_inches="tight") 
            plt.close()
            image.append(imageio.imread(graf+regfile+"CAS.jpg"))
        imageio.mimsave(gifs+regfile+"CAS.gif",image, loop = 1)
        # Mortes por semana
        #
        image = []
        for i in range(0, N_s):         
            plt.grid(False)
            plt.ylim(0,np.amax(D_week))
            T_week_i = T_week[:i]
            D_week_i = D_week[:i]            
            plt.bar(T_week_i,D_week_i)
            plt.xlabel("Semanas desde o primeiro caso")
            plt.ylabel("Mortes")
            plt.title("Mortes por semana - "+reg+" - "+date[6:8]+"/"+date[4:6]+"/"+date[0:4])
            plt.savefig(graf+regfile+"MS.jpg",bbox_inches="tight") 
            plt.close()
            image.append(imageio.imread(graf+regfile+"MS.jpg"))
        imageio.mimsave(gifs+regfile+"MS.gif",image, loop = 1)        

        plt.close()
            
    else:
        # Novos casos por semana
        blue_list = ["blue" for i in range(0,N_s)]
        image = []
        for i in range(0, N_s): 
            plt.ylim(0,np.amax(R_week))
            T_week_i = T_week[:i]
            R_week_i = R_week[:i]            
            plt.bar(T_week_i,R_week_i)
            plt.xlabel("Semanas desde o primeiro caso")
            plt.ylabel("Casos")
            plt.title("Casos por semana - "+reg+" - "+date[6:8]+"/"+date[4:6]+"/"+date[0:4])
            plt.savefig(graf+regfile+"CAS.jpg",bbox_inches="tight") 
            plt.close()
            image.append(imageio.imread(graf+regfile+"CAS.jpg"))            
        plt.bar(T_week,np.concatenate((R_week,np.array([R_week_rem]))),color = np.concatenate((np.array(blue_list),np.array(["lightblue"]))))
        plt.xlabel("Semanas desde o primeiro caso")
        plt.ylabel("Casos")
        plt.title("Casos por semana - "+reg+" - "+date[6:8]+"/"+date[4:6]+"/"+date[0:4])
        plt.savefig(graf+regfile+"CAS.jpg",bbox_inches="tight") 
        plt.close()
        image.append(imageio.imread(graf+regfile+"CAS.jpg"))
        imageio.mimsave(gifs+regfile+"CAS.gif",image, loop = 1)    
        plt.close() 
            
        # Mortes por semana
        #
        image = []
        for i in range(0, N_s): 
            plt.ylim(0,np.amax(D_week))
            T_week_i = T_week[:i]
            D_week_i = D_week[:i]            
            plt.bar(T_week_i,D_week_i)
            plt.xlabel("Semanas desde o primeiro caso")
            plt.ylabel("Mortes")
            plt.title("Mortes por semana - "+reg+" - "+date[6:8]+"/"+date[4:6]+"/"+date[0:4])
            plt.savefig(graf+regfile+"MS.jpg",bbox_inches="tight") 
            plt.close()
            image.append(imageio.imread(graf+regfile+"MS.jpg"))            
        plt.bar(T_week,np.concatenate((D_week,np.array([D_week_rem]))),color = np.concatenate((np.array(blue_list),np.array(["lightblue"]))))
        plt.xlabel("Semanas desde o primeiro caso")
        plt.ylabel("Mortes")
        plt.title("Mortes por semana - "+reg+" - "+date[6:8]+"/"+date[4:6]+"/"+date[0:4])
        plt.savefig(graf+regfile+"MS.jpg",bbox_inches="tight") 
        plt.close()
        image.append(imageio.imread(graf+regfile+"MS.jpg"))
        imageio.mimsave(gifs+regfile+"MS.gif",image, loop = 1)    
        plt.close()         
        
    return 

def write_js(html_file,R_permil_global,D_permil_global,reglist,R0list,N_max,date,linecsv,R_smooth2,dR_smooth2,gamma1,gamma2,alpha):
    
    for reg in reglist:
        print(reg)
        res = read_csv_data(reg,linecsv)
        R_raw = res['R_raw'] 
        D_raw = res['D_raw']
        Popul = res['Popul']
        N_k = res['N_k']    
        R_permil_global.append(1.0e6*R_raw/Popul)
        D_permil_global.append(1.0e6*D_raw/Popul)    
        if N_k>N_max:
            N_max = N_k
        R0_est_int_0 , R0_est_int_1 = R0int(R_smooth2,dR_smooth2,Popul,gamma1,gamma2,alpha)
        r_avg = np.mean(np.concatenate( (R0_est_int_0[N_k-17:N_k-3] , R0_est_int_1[N_k-17:N_k-3] ) ) )
        R0list[reglist.index(reg)] = r_avg   


    T = np.linspace(0,N_max-1,N_max)
    Y = np.zeros((N_max,len(reglist)))

    arg = np.argsort(R0list) 

    for i in range (0,len(reglist)):
        Y1 = R_permil_global[i]
        if Y1.size < N_max:
            Y[:,i] = np.concatenate( (np.zeros(N_max - Y1.size) ,Y1))
        else:
            Y[:,i] = Y1

    html_file.write('<br> \n')

    html_file.write('<hr> \n')

    html_file.write('<big><big><span style="font-weight: bold;"> Casos e mortes por milhão por estados. Explore com o mouse, clique para realçar. </span></big></big><br> \n')


    html_file.write('<html> \n')
    html_file.write('<head> \n')
    html_file.write('<script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script> \n')
    html_file.write('<script> \n')
    html_file.write(' \n')
    html_file.write("google.charts.load('current', {packages: ['corechart', 'line']} ); \n");
    html_file.write('google.charts.setOnLoadCallback(drawChart); \n')
    html_file.write(' \n')
    html_file.write("function drawChart() { \n");
    html_file.write("      var data = new google.visualization.DataTable(); \n")
    html_file.write("      data.addColumn('number', 'Dias'); \n");
    for i in range (0,len(reglist)):
        html_file.write("      data.addColumn('number', '"+reglist[arg[len(reglist)-1-i]][0]+", r0 = "+'{0:.2f}'.format(R0list[arg[len(reglist)-1-i]]).replace(".",",")+"'); \n")
    html_file.write(' \n')

    html_file.write("      data.addRows([  \n")
    for i in range(0,N_max):
        linedata = str(T[i])
        for j in range (0,len(reglist)):
            linedata = linedata+","+str(Y[i,arg[len(reglist)-1-j]])
        html_file.write("        ["+linedata+"], \n")
    html_file.write('      ]); \n')
    html_file.write(' \n')
    html_file.write("      var options = {\n")
    html_file.write("        title: 'Casos por milhão - "+date[6:8]+"/"+date[4:6]+"/"+date[0:4]+"',\n")
    html_file.write("	width: 900,\n")
    html_file.write("        height: 700,\n")
    html_file.write("	       series: { \n") 
    for i in range (0,len(reglist)-1):
        html_file.write(str(i)+": { lineWidth: 1 }, \n")
    html_file.write(str(len(reglist)-1)+": { lineWidth: 1 } \n")
    html_file.write("        },\n")
    html_file.write("        hAxis: {title: 'Dias'},\n")
    html_file.write("        vAxis: {title: 'Casos por milhão', scaleType: 'log'} \n")
    html_file.write("        };\n")
    html_file.write(' \n')
    html_file.write("      var chart = new google.visualization.LineChart(document.getElementById('casos_div'));\n")
    html_file.write("      google.visualization.events.addListener(chart, 'select', function() { highlightLine(chart,data, options); });\n")
    html_file.write("      chart.draw(data,  options);\n")
    html_file.write("    }\n")
    html_file.write("function highlightLine(chart,data,options) {\n")
    html_file.write("    var selectedLineWidth = 6;\n")
    html_file.write("    var selectedItem = chart.getSelection()[0];\n")
    html_file.write("    //reset series line width to default value\n")
    html_file.write("    for(var i in options.series) {options.series[i].lineWidth = 1;}\n")
    html_file.write("    options.series[selectedItem.column-1].lineWidth = selectedLineWidth; //set selected line width\n")
    html_file.write("    chart.draw(data, options);   //redraw\n")
    html_file.write("}\n")
    html_file.write("</script>\n")
    html_file.write("</head>\n")
    html_file.write('<div id="casos_div"></div>\n')



    for i in range (0,len(reglist)):
        Y1 = D_permil_global[i]
        if Y1.size < N_max:
            Y[:,i] = np.concatenate( (np.zeros(N_max - Y1.size) ,Y1))
        else:
            Y[:,i] = Y1
        
        
    html_file.write('<html> \n')
    html_file.write('<head> \n')
    html_file.write('<script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script> \n')
    html_file.write('<script> \n')
    html_file.write(' \n')
    html_file.write("google.charts.load('current', {packages: ['corechart', 'line']} ); \n");
    html_file.write('google.charts.setOnLoadCallback(drawChart); \n')
    html_file.write(' \n')
    html_file.write("function drawChart() { \n");
    html_file.write("      var data = new google.visualization.DataTable(); \n")
    html_file.write("      data.addColumn('number', 'Dias'); \n");
    for i in range (0,len(reglist)):
        html_file.write("      data.addColumn('number', '"+reglist[arg[len(reglist)-1-i]][0]+", r0 = "+'{0:.2f}'.format(R0list[arg[len(reglist)-1-i]]).replace(".",",")+"'); \n")
    html_file.write(' \n')

    html_file.write("      data.addRows([  \n")
    for i in range(0,N_max):
        linedata = str(T[i])
        for j in range (0,len(reglist)):
            linedata = linedata+","+str(Y[i,arg[len(reglist)-1-j]])
        html_file.write("        ["+linedata+"], \n")
    html_file.write('      ]); \n')
    html_file.write(' \n')
    html_file.write("      var options = {\n")
    html_file.write("        title: 'Mortes por milhão - "+date[6:8]+"/"+date[4:6]+"/"+date[0:4]+"',\n")
    html_file.write("	width: 900,\n")
    html_file.write("        height: 700,\n")
    html_file.write("	       series: { \n") 
    for i in range (0,len(reglist)-1):
        html_file.write(str(i)+": { lineWidth: 1 }, \n")
    html_file.write(str(len(reglist)-1)+": { lineWidth: 1 } \n")
    html_file.write("        },\n")
    html_file.write("        hAxis: {title: 'Dias'},\n")
    html_file.write("        vAxis: {title: 'Mortes por milhão', scaleType: 'log'} \n")
    html_file.write("        };\n")
    html_file.write(' \n')
    html_file.write("      var chart = new google.visualization.LineChart(document.getElementById('mortes_div'));\n")
    html_file.write("      google.visualization.events.addListener(chart, 'select', function() { highlightLine(chart,data, options); });\n")
    html_file.write("      chart.draw(data,  options);\n")
    html_file.write("    }\n")
    html_file.write("function highlightLine(chart,data,options) {\n")
    html_file.write("    var selectedLineWidth = 6;\n")
    html_file.write("    var selectedItem = chart.getSelection()[0];\n")
    html_file.write("    //reset series line width to default value\n")
    html_file.write("    for(var i in options.series) {options.series[i].lineWidth = 1;}\n")
    html_file.write("    options.series[selectedItem.column-1].lineWidth = selectedLineWidth; //set selected line width\n")
    html_file.write("    chart.draw(data, options);   //redraw\n")
    html_file.write("}\n")
    html_file.write("</script>\n")
    html_file.write("</head>\n")
    html_file.write('<div id="mortes_div"></div>\n')

    return

def graf(reg,linecsv,gamma1,gamma2,alpha,reglist,date,graf,gifs,
                dict_estados):
    
    print(reg)
    res = read_csv_data(reg,linecsv)

    R_raw = res['R_raw'] 
    D_raw = res['D_raw'] 
    N_k = res['N_k']
    First_Day = res['First_Day']
    Last_Day = res['Last_Day']
    Popul = res['Popul'] 

    N_s = int(N_k/7)
    N_d = N_k-7*N_s
    
    dR_raw = np.zeros(N_k)
    
    for i in range (1,N_k):
        dR_raw[i] = R_raw[i] - R_raw[i-1]   
    
    dD_raw = np.zeros(N_k)
    
    for i in range (1, N_k):
        dD_raw[i] = D_raw[i] - D_raw[i-1]  

#
# Suavização: 2 iterações da média móvel   
#
    R_smooth2 = smooth(R_raw,3,2)

#
# Suavização: 4 iterações da média móvel   
#
    R_smooth4 = smooth(R_raw,3,4)
    
    D_smooth4 = smooth(D_raw,3,4)

    dR_smooth2 = np.zeros(N_k)
    for i in range (1,N_k):
        dR_smooth2[i] = R_smooth2[i] - R_smooth2[i-1]
    
    dR_smooth4 = np.zeros(N_k)
    for i in range (1,N_k):
        dR_smooth4[i] = R_smooth4[i] - R_smooth4[i-1]
    
    d2R_smooth4 = np.zeros(N_k)
    for i in range (1,N_k):
        d2R_smooth4[i] = dR_smooth4[i] - dR_smooth4[i-1]
        
    dD_smooth4 = np.zeros(N_k)
    for i in range(1,N_k):
        dD_smooth4[i] = D_smooth4[i] - D_smooth4[i-1]
    
    R_prev = np.zeros(5)#previsão de novos casos
    a,b,r_value, p_value, std_err =  scipy.stats.linregress(np.linspace(-9,0,10),R_raw[N_k-10:N_k])
    for j in range (0,5):
        R_prev[j] = a*(j+1) + R_raw[N_k-1]

    R0_est_dif_0 , R0_est_dif_1 = R0dif(R_smooth4,dR_smooth4,d2R_smooth4,Popul,gamma1,gamma2,alpha)
    R0_est_int_0 , R0_est_int_1 = R0int(R_smooth2,dR_smooth2,Popul,gamma1,gamma2,alpha)

    r_avg = np.mean(np.concatenate( (R0_est_int_0[N_k-17:N_k-3] , R0_est_int_1[N_k-17:N_k-3] ) ) )
    std_err = np.std(np.concatenate( (R0_est_int_0[N_k-17:N_k-3] , R0_est_int_1[N_k-17:N_k-3])  ) )

    R01 = min(R0_est_int_0[N_k-4],R0_est_int_1[N_k-4])
    R02 = max(R0_est_int_0[N_k-4],R0_est_int_1[N_k-4]) 
    
    nR = 1 - 1/r_avg 

    regfile = hashlib.md5(bytes(reg[0]+reg[1]+date,'utf-8')).hexdigest()  

    if reg[1] == "":
        regstr = reg[0]
    else:
        regstr = reg[1]+' - '+reg[0]
        
        
    drawR0thumb(R0_est_dif_0,R0_est_dif_1,regstr,regfile,date)        
    drawCA(R_raw,R_smooth4,regstr,regfile,date,graf,gifs)
    drawMA(D_raw,D_smooth4,regstr,regfile,date,graf,gifs)
    drawNC(dR_raw,dR_smooth4,regstr,regfile,date,graf,gifs)
    drawPM(R_raw,D_raw,Popul,regstr,regfile,date) 
    drawR0dif(R0_est_dif_0,R0_est_dif_1,regstr,regfile,date)
    drawR0int(R0_est_int_0,R0_est_int_1,regstr,regfile,date)
    drawMU(R_smooth4,dR_smooth4,Popul,gamma1,gamma2,alpha,regstr,regfile,date)
    drawCAS(R_raw,D_raw,N_s,N_d,regstr,regfile,date,graf,gifs)
    drawNM(dD_raw,dD_smooth4,regstr,regfile,date,graf,gifs)
    drawNM_NC(dR_raw,dD_raw,regstr,regfile,date)
        
    html_file_local = codecs.open(regfile+".html","w", encoding="iso-8859-1")   
  
    write_dict = { \
     'html_file'  : html_file_local  , \
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
    update_date = dict_estados[reg[0]]

    write_analise(write_dict,update_date,gifs)
    
    html_file_local.close()

    wkhtmltopdf = "wkhtmltopdf --quiet "+regfile+".html "+regfile+".pdf"
    
    os.system(wkhtmltopdf)
    
    return

def graf_brasil(reg,linecsv,gamma1,gamma2,alpha,reglist,date,graf,gifs,
                dict_estados,html_file):
    
    print(reg)
    res = read_csv_data(reg,linecsv)

    R_raw = res['R_raw'] 
    D_raw = res['D_raw'] 
    N_k = res['N_k']
    First_Day = res['First_Day']
    Last_Day = res['Last_Day']
    Popul = res['Popul'] 

    N_s = int(N_k/7)
    N_d = N_k-7*N_s
    
    dR_raw = np.zeros(N_k)
    
    for i in range (1,N_k):
        dR_raw[i] = R_raw[i] - R_raw[i-1]   
    
    dD_raw = np.zeros(N_k)
    
    for i in range (1, N_k):
        dD_raw[i] = D_raw[i] - D_raw[i-1]  

#
# Suavização: 2 iterações da média móvel   
#
    R_smooth2 = smooth(R_raw,3,2)

#
# Suavização: 4 iterações da média móvel   
#
    R_smooth4 = smooth(R_raw,3,4)
    
    D_smooth4 = smooth(D_raw,3,4)

    dR_smooth2 = np.zeros(N_k)
    for i in range (1,N_k):
        dR_smooth2[i] = R_smooth2[i] - R_smooth2[i-1]
    
    dR_smooth4 = np.zeros(N_k)
    for i in range (1,N_k):
        dR_smooth4[i] = R_smooth4[i] - R_smooth4[i-1]
    
    d2R_smooth4 = np.zeros(N_k)
    for i in range (1,N_k):
        d2R_smooth4[i] = dR_smooth4[i] - dR_smooth4[i-1]
        
    dD_smooth4 = np.zeros(N_k)
    for i in range(1,N_k):
        dD_smooth4[i] = D_smooth4[i] - D_smooth4[i-1]
    
    R_prev = np.zeros(5)
    a,b,r_value, p_value, std_err =  scipy.stats.linregress(np.linspace(-9,0,10),R_raw[N_k-10:N_k])
    for j in range (0,5):
        R_prev[j] = a*(j+1) + R_raw[N_k-1]

    R0_est_dif_0 , R0_est_dif_1 = R0dif(R_smooth4,dR_smooth4,d2R_smooth4,Popul,gamma1,gamma2,alpha)
    R0_est_int_0 , R0_est_int_1 = R0int(R_smooth2,dR_smooth2,Popul,gamma1,gamma2,alpha)

    r_avg = np.mean(np.concatenate( (R0_est_int_0[N_k-17:N_k-3] , R0_est_int_1[N_k-17:N_k-3] ) ) )
    std_err = np.std(np.concatenate( (R0_est_int_0[N_k-17:N_k-3] , R0_est_int_1[N_k-17:N_k-3])  ) )

    
    R01 = min(R0_est_int_0[N_k-4],R0_est_int_1[N_k-4])
    R02 = max(R0_est_int_0[N_k-4],R0_est_int_1[N_k-4]) 
    
    nR = 1 - 1/r_avg 

    regfile = hashlib.md5(bytes(reg[0]+reg[1]+date,'utf-8')).hexdigest()  

    regstr = reg[0]
            
    drawR0thumb(R0_est_dif_0,R0_est_dif_1,regstr,regfile,date)        
    drawCA(R_raw,R_smooth4,regstr,regfile,date,graf,gifs)
    drawMA(D_raw,D_smooth4,regstr,regfile,date,graf,gifs)
    drawNC(dR_raw,dR_smooth4,regstr,regfile,date,graf,gifs)
    drawPM(R_raw,D_raw,Popul,regstr,regfile,date) 
    drawR0dif(R0_est_dif_0,R0_est_dif_1,regstr,regfile,date)
    drawR0int(R0_est_int_0,R0_est_int_1,regstr,regfile,date)
    drawMU(R_smooth4,dR_smooth4,Popul,gamma1,gamma2,alpha,regstr,regfile,date)
    drawCAS(R_raw,D_raw,N_s,N_d,regstr,regfile,date,graf,gifs)
    drawNM(dD_raw,dD_smooth4,regstr,regfile,date,graf,gifs)
    drawNM_NC(dR_raw,dD_raw,regstr,regfile,date)
        
    html_file_local = codecs.open(regfile+".html","w", encoding="iso-8859-1")    
          
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

    write_analise(write_dict,update_date,gifs)
    
    write_dict['html_file'] = html_file_local
    write_analise(write_dict,update_date,gifs)

    html_file_local.close()

    wkhtmltopdf = "wkhtmltopdf --quiet "+regfile+".html "+regfile+".pdf"
    
    os.system(wkhtmltopdf)
    
    return R_smooth2 , dR_smooth2    
    




