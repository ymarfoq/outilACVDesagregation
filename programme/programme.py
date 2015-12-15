from SimaPro_reader import SimaPro_reader
from transformation_matrices import transformation_matrices
from print_matrices_informations import print_matrices_informations
from scipy.linalg import inv
from scipy.sparse import identity, lil_matrix
from scipy.sparse.linalg import spsolve
from numpy import matrix, log, sign, loadtxt, genfromtxt, transpose
from fix_inverse import fix_inverse
from calculate_all_scores import calculate_all_scores
from calcul_parameters import calcul_parameters
from MC_correlated_preparation import MC_correlated_preparation
from MC_nocorrelated_preparation import MC_nocorrelated_preparation
from MC import MC
from calcul_vcv import calcul_vcv
from build_final_demand_vector import build_final_demand_vector
from systematic_disaggregation_UP import systematic_disaggregation_UP
from construct_UP_list_desag import construct_UP_list_desag
from build_mat_desag import build_mat_desag
from print_results import print_results
from tree import tree
import csv
import re
import os
import shutil
from Tkinter import *
import ttk
import time
import threading
from multiprocessing import Pool

if os.getcwd()[-6:]=="python":
	path=re.sub("python","",os.getcwd())#location of the courant folder
else:
	path=re.sub("programme","",os.getcwd())#location of the courant folder

print "running..."
def selectProject():
	global project_name
	project_name=projectName.get()
	projectNameList.destroy()
	selectProjectButton.destroy()
	if os.path.isdir(path+projectName.get()):
		infos=loadtxt(os.path.join(path,project_name,"info.csv"), delimiter="||", dtype=str)
		global impact_method
		impact_method=str(infos[4][17:])
		methodNameList.destroy()
		selectMethodButton.destroy()
		Label(nameMethodFrame,text=str(infos[4][17:])).pack(side=LEFT)	
		global database
		database=str(infos[3][11:])
		databaseNameList.destroy()
		selectDatabaseButton.destroy()
		Label(nameDatabaseFrame,text=str(infos[3][11:])).pack(side=LEFT)	
		global disaggregation_criterion
		disaggregation_criterion=float(infos[2][26:-1])/100
		criterion.destroy()
		criterionButton.destroy()
		Label(disaggregationCriterionFrame,text=infos[2][26:]).pack(side=LEFT)
		newproject=False
	else:
		os.mkdir(path+projectName.get())
		os.mkdir(os.path.join(path,project_name,"correlated_impacts"))
		os.mkdir(os.path.join(path,project_name,"nocorrelated_impacts"))
		os.mkdir(os.path.join(path,project_name,"trees"))
		os.mkdir(os.path.join(path,project_name,"variance_covariance"))
		shutil.copyfile(os.path.join(path,"programme","style.css"), os.path.join(path,project_name,"trees","style.css"))
		shutil.copyfile(os.path.join(path,"programme","fleche_bas.png"), os.path.join(path,project_name,"trees","fleche_bas.png"))
		shutil.copyfile(os.path.join(path,"programme","fleche_haut.png"), os.path.join(path,project_name,"trees","fleche_haut.png"))
		shutil.copyfile(os.path.join(path,"programme","script.js"), os.path.join(path,project_name,"trees","script.js"))
		shutil.copyfile(os.path.join(path,"programme","croix.png"), os.path.join(path,project_name,"trees","croix.png"))	
	
	Label(NameProjectFrame,text=projectName.get()).pack(side=LEFT)
	
def selectMethod():
	methodNameList.destroy()
	selectMethodButton.destroy()
	Label(nameMethodFrame,text=methodName.get()).pack(side=LEFT)	
	global impact_method
	impact_method=methodName.get()

def selectDatabase():
	databaseNameList.destroy()
	selectDatabaseButton.destroy()
	Label(nameDatabaseFrame,text=databaseName.get()).pack(side=LEFT)	
	global database
	database=databaseName.get()
	
def selectIterationsNumber():
	global iterations
	iterations=int(iterations.get())
	iterationNumber.destroy()
	iterationButton.destroy()
	Label(numberIterationFrame,text=iterations).pack(side=LEFT)

def selectDisaggregationCriterion():
	global disaggregation_criterion
	disaggregation_criterion=float(disaggregationCriterion.get())/100
	criterion.destroy()
	criterionButton.destroy()
	Label(disaggregationCriterionFrame,text=str(disaggregation_criterion*100)+"%").pack(side=LEFT)

def cleaning(up,simulation,number_iteration_fini, typeOfCorrelation):
	try:
		lastIteration=genfromtxt(os.path.join(path,project_name,typeOfCorrelation,str(up)+".csv"), delimiter=",", usecols = (0))[-1]
	except:
		lastIteration=0
	nouveau=csv.writer(open(os.path.join(path,project_name,typeOfCorrelation,str(up)+".csv"), "ab"))
	
	tirage=loadtxt(os.path.join(path,project_name,typeOfCorrelation+str(simulation),str(up)+".csv"),delimiter=",")
	if number_iteration_fini:
		for row in tirage[:number_iteration_fini]:
			nouveau.writerow([str(row[0]+lastIteration)]+list(row[1:]))
	else:
		for row in tirage:
			nouveau.writerow([str(row[0]+lastIteration)]+list(row[1:]))
	lastIteration+=tirage[-1,0]+1
	os.remove(os.path.join(path,project_name,typeOfCorrelation+str(simulation),str(up)+".csv"))
  
  

def cleaningAll():
	#on lit le fichier info comme une liste dans laquelle chaque element correspond a une ligne (delimiter=||| jamais trouve), on divise ensuite la ligne 24 qui correspond a la liste des processus pour avoir le nombre total de processus
	number_process=len(loadtxt(os.path.join(path,project_name,"info.csv"), delimiter="|||", dtype=str)[24].split(","))
	for simulation in [ e[18:] for e in os.listdir(os.path.join(path,project_name)) if e[:18]=="correlated_impacts" and e<>"correlated_impacts"]:
		number_iteration_fini=len(loadtxt(os.path.join(path,project_name,"correlated_impacts"+str(simulation),"0.csv"), delimiter="|", dtype=str))-1
		for i in range(number_process):
			cleaning(i,simulation,number_iteration_fini, "correlated_impacts")
	for essai in [ e for e in os.listdir(os.path.join(path,project_name)) if e[:18]=="correlated_impacts" and e<>"correlated_impacts"]:
		os.rmdir(os.path.join(path,project_name,essai))
	
	for simulation in [ e[20:] for e in os.listdir(os.path.join(path,project_name)) if e[:20]=="nocorrelated_impacts" and e<>"nocorrelated_impacts"]:
		for i in range(number_process):
			try:
				cleaning(i,simulation,False, "nocorrelated_impacts")
			except:
				1
	for essai in [ e for e in os.listdir(os.path.join(path,project_name)) if e[:20]=="nocorrelated_impacts" and e<>"nocorrelated_impacts"]:
		os.rmdir(os.path.join(path,project_name,essai))
	
	
	UP_list=loadtxt(os.path.join(path,project_name,"info.csv"), delimiter="|||", dtype=str)[25][1:-1].split("\",\"")
	CF_categories=[name[:name.find(" (")] for name in loadtxt(os.path.join(path,project_name,"info.csv"), delimiter="|||", dtype=str)[6][1:-1].split(" , ")]
	impact_method=loadtxt(os.path.join(path,project_name,"info.csv"), delimiter="|||", dtype=str)[4][17:]
	
	sigma_correlated, mu_correlated, sign_correlated=calcul_parameters(UP_list, os.path.join(path,project_name,"correlated_impacts"), len(CF_categories))
		
	results_cor = csv.writer(open(os.path.join(path,project_name,"Monte-Carlo_results_correle.csv"), "wb"))
	results_cor.writerow(["index", "processus"]+["sign "+category for category in CF_categories]+["mu "+category for category in CF_categories]+["sigma "+category for category in CF_categories])
	for up in range(len(UP_list)-4):
		results_cor.writerow([up, UP_list[up]]+[ssign for ssign in sign_correlated[up,:].tolist()]+[mmu for mmu in mu_correlated[up,:].tolist()]+[sigma for sigma in sigma_correlated[up,:].tolist()])
		
 	sigma_nocorrelated, mu_nocorrelated, sign_nocorrelated=calcul_parameters(UP_list, os.path.join(path,project_name,"nocorrelated_impacts"), len(CF_categories))
		
	results_nocor = csv.writer(open(os.path.join(path,project_name,"Monte-Carlo_results_nocorrele.csv"), "wb"))
	results_nocor.writerow(["index", "processus"]+["sign "+category for category in CF_categories]+["mu "+category for category in CF_categories]+["sigma "+category for category in CF_categories])
	for up in range(len(UP_list)-4):
		try:
			results_nocor.writerow([up, UP_list[up]]+[ssign for ssign in sign_nocorrelated[up,:].tolist()]+[mmu for mmu in mu_nocorrelated[up,:].tolist()]+[sigma for sigma in sigma_nocorrelated[up,:].tolist()])
		except:
			results_nocor.writerow([up, UP_list[up]])

###Calculation of the cariance-covariance matrices
	calcul_vcv(UP_list, impact_method, CF_categories, os.path.join(path,project_name))
 	
def calcul():
	t1=threading.Thread(target=calculExecution)
	t1.start()

def calculExecution():
	'''
	Construction of technology and intervention matrices with uncertainties informations
	Construction of Caracterisation facteurs matrix 
	'''
	
	runButton.config(state="disabled")
	
	global pb_hD
	
	system_filename = os.path.join(path,"programme","..","databases",database) #export from Simapro

	infoFrame1=Frame(informationsFrame)
	infoFrame1.pack()
	Label(infoFrame1,text="Reading the database and constructing the matrices...").pack(side=LEFT)
	
	
	(system_meta_info, UP_meta_info, UP_list, EF_list,all_flow, technology_matrix, 
		intervention_matrix, CF_matrices, CF_categories, CF_units, EF_unit, 
		unit_converter, infrastructure_rescale, uncertainty_info) = SimaPro_reader(system_filename, impact_method)

	Label(infoFrame1,text="Done").pack()

	CF_matrix = CF_matrices[impact_method]
	CF_categories=CF_categories[impact_method]
	CF_units=CF_units[impact_method]
	CF_categories_name=[ re.sub("\W","_",cat) for cat in CF_categories]
	
	EF_by_number = {}
	for (compartment, substance, subcompartment) in EF_list:
		EF = [compartment, substance, subcompartment]
		EF_number = EF_list.index(EF)
		EF = (compartment, substance, subcompartment)
		EF_by_number[EF_number] = EF


	###Transformation of the technology and intervention matrices for testing the fonctionnality of the algorithme.
	infoFrame2=Frame(informationsFrame)
	infoFrame2.pack()
	Label(infoFrame2,text="transformating matrices for tests ...").pack(side=LEFT)
	(technology_matrix,intervention_matrix,uncertainty_info, UP_list, CF_transformed)=transformation_matrices(technology_matrix,intervention_matrix,uncertainty_info, UP_list, CF_matrix)
	Label(infoFrame2,text="Done").pack()

	
	print_results(path+project_name, project_name, UP_list, EF_list, database, impact_method, CF_categories, CF_units, iterations, disaggregation_criterion, uncertainty_info, CF_matrix)


	###Calculation of the determinists scores
	infoFrame3=Frame(informationsFrame)
	infoFrame3.pack()
	Label(infoFrame3,text="Calculating deterministic scores ...").pack(side=LEFT)
	t0=time.time()
	#inverse_technology_matrix=spsolve(technology_matrix, identity(technology_matrix.shape[0]))
	inverse_technology_matrix = inv(technology_matrix.todense())
	tinv=time.time()-t0
	#print "temps d'inversion : "+str(tinv)
	Z = (identity(len(technology_matrix.todense())) - technology_matrix)
	inverse_technology_matrix = fix_inverse(Z, inverse_technology_matrix)
	intensity_matrix = matrix(intervention_matrix.dot(inverse_technology_matrix))
	all_system_scores, all_unit_scores = calculate_all_scores(identity(len(technology_matrix.todense())),intensity_matrix, intervention_matrix, CF_matrix)
	
	results_det = csv.writer(open(os.path.join(path,project_name,"results_det.csv"), "wb"))
	results_det.writerow(["index", "processus"]+["impact "+category for category in CF_categories])
	for up in range(len(UP_list)-4):
		results_det.writerow([up, UP_list[up]]+[impact[0] for impact in all_system_scores[:,up].tolist()])
		
 
	Label(infoFrame3,text="Done").pack()
	
	if correlatedMC.get():

		###Monte-Carlo in the correlated case and storage of the matrices (laws'parameters)
		Label(informationsFrame,text="Uncertainty analysis under a fully-correlated assumption...").pack()
		
		pb_hD.pack()
		
		essai=0
		while 1:
			try:
				os.mkdir(os.path.join(path,project_name,"correlated_impacts"+str(essai)))
				break
			except:
				essai+=1
			
						
		(variables_technologique, variables_intervention)=MC_correlated_preparation(technology_matrix, intervention_matrix, uncertainty_info['technology'], uncertainty_info['intervention'])
		MC(variables_technologique, variables_intervention, CF_matrix, CF_categories_name, iterations, UP_list, "all", os.path.join(path,project_name,"correlated_impacts"+str(essai)), [], progress)

		infoFrame4=Frame(informationsFrame)
		infoFrame4.pack()
		Label(infoFrame4,text="Done ...").pack(side=LEFT)	

	if nocorrelatedMC.get():
		
		sigma_correlated, mu_correlated, sign_correlated=calcul_parameters(UP_list, os.path.join(path,project_name,"correlated_impacts"), len(CF_categories))
		
		essai=0
		while 1:
			try:
				os.mkdir(os.path.join(path,project_name,"nocorrelated_impacts"+str(essai)))
				break
			except:
				essai+=1
		
		###Monte-Carlo in the correlated case and storage of the matrices (laws'parameters)
		Label(informationsFrame,text="Uncertainty analysis under a fully-uncorrelated assumption...").pack()
				
		full_results_UP = {}
		full_results_EF = {}
		level_reached = {}
		system_scores = {}
		child_list = {}
		score_list_EF = {}
		coefficient_list = {}
		link_UP_EF_full_result = {}
		systems=[]
		for proc in UP_list:
			systems.append({proc:1})
		
		processRunned=Label(informationsFrame,text="")
		processRunned.pack()
		
		for system_number in range(nocorrBegin.get(),min(nocorrEnd.get(),len(UP_list)-4)): #disaggregation for every system
			
			processRunned.config(text="Process "+str(system_number))
			pb_hD.pack()
			
			full_results_UP = {}
			full_results_EF = {}
			level_reached = {}
			system_scores = {}
			child_list = {}
			score_list_EF = {}
			coefficient_list = {}
			link_UP_EF_full_result = {}
			final_demand_vector = build_final_demand_vector(systems[system_number], UP_list)
			start_time = time.time()
			full_results_UP = {}
			level_reached = {}
			
			#Desagregation of the system
			
			full_results_UP, level_reached, system_scores = systematic_disaggregation_UP(disaggregation_criterion,full_results_UP, level_reached, system_scores,UP_meta_info, UP_list, EF_list, technology_matrix, intervention_matrix, CF_matrix, CF_categories, EF_unit, uncertainty_info, intensity_matrix, Z, all_system_scores, all_unit_scores, impact_method, final_demand_vector, system_number,systems)
			
			UP_list_desag=construct_UP_list_desag(full_results_UP,UP_list)
			tree(UP_list_desag, UP_meta_info, impact_method, CF_categories, all_system_scores, all_unit_scores, CF_units, os.path.join(path,project_name,"trees"))

			(variables_technologique, variables_intervention)=MC_nocorrelated_preparation(technology_matrix, intervention_matrix, uncertainty_info['technology'], uncertainty_info['intervention'], UP_list, UP_list_desag, mu_correlated, sign_correlated, sigma_correlated)
			MC(variables_technologique, variables_intervention, CF_transformed, CF_categories_name, iterations, UP_list_desag, system_number, os.path.join(path,project_name,"nocorrelated_impacts"+str(essai)), systems, progress)
			
		infoFrame5=Frame(informationsFrame)
		infoFrame5.pack()
		Label(infoFrame5,text="Printing parameters ...").pack(side=LEFT)
		
		Label(infoFrame5,text="Done").pack(side=LEFT)
		
if 1: 
	###
	###  Construction of the from threading import Threadinterface
	###

	fenetre = Tk()#Principal Window

	fenetre.title('.....')#Title

	principalFrame=Frame(fenetre, borderwidth=5, width=500)
	principalFrame.pack()


	###Choix du project
	NameProjectFrame=Frame(principalFrame)
	NameProjectFrame.pack()

	Label(NameProjectFrame,text="Project name : ").pack(side=LEFT)

	projectName = StringVar()
	projectNameList = ttk.Combobox(NameProjectFrame, width=20, textvariable=projectName)
	projectNameList['values'] =tuple([proj for proj in os.listdir(path) if proj not in["databases","programme","python", "run.bat", "readme.doc"]])
	projectNameList.current(0)
	projectNameList.pack(side=LEFT)

	selectProjectButton=Button(NameProjectFrame, text="select", command=selectProject)
	selectProjectButton.pack()    
	###Fin du choix du projet

	###choix de la methode
	impact_methodes = [impactName for impactName in os.listdir(os.path.join(path,"databases", "impactMethods")) if impactName[:11]<>"impact2002+" and impactName[:2]<>'IW']+["IMPACT2002+ midpoint", "IMPACT2002+ endpoint", 'IMPACT World midpoint', 'IMPACT World endpoint']
	databases = [db for db in os.listdir(os.path.join(path,"databases"))]
	#impact_methodes=['EcodEx','IMPACT2002+ midpoint', 'IMPACT2002+ endpoint', 'Climat Change - Impact2002+', 'IMPACT World midpoint', 'IMPACT World endpoint', 'Recipe midpoint']
	
	nameMethodFrame=Frame(principalFrame)
	nameMethodFrame.pack()

	nameDatabaseFrame=Frame(principalFrame)
	nameDatabaseFrame.pack()

	Label(nameMethodFrame,text="Impact method : ").pack(side=LEFT)
	Label(nameDatabaseFrame,text="Database : ").pack(side=LEFT)

	methodName = StringVar()
	methodNameList = ttk.Combobox(nameMethodFrame, width=50, textvariable=methodName)
	methodNameList['values'] =tuple(impact_methodes)
	methodNameList.current(0)
	methodNameList.pack(side=LEFT)

	databaseName = StringVar()
	databaseNameList = ttk.Combobox(nameDatabaseFrame, width=50, textvariable=databaseName)
	databaseNameList['values'] =tuple(databases)
	databaseNameList.current(0)
	databaseNameList.pack(side=LEFT)

	selectMethodButton=Button(nameMethodFrame, text="select", command=selectMethod)
	selectMethodButton.pack()
	selectDatabaseButton=Button(nameDatabaseFrame, text="select", command=selectDatabase)
	selectDatabaseButton.pack()
	###Fin choix methode

	###choix du nombre d'iterations
	numberIterationFrame=Frame(principalFrame)
	numberIterationFrame.pack()

	iterations=StringVar()

	Label(numberIterationFrame,text="Number of iterations : ").pack(side=LEFT)

	iterationNumber= Entry(numberIterationFrame, width=5, textvariable=iterations)
	iterationNumber.insert(0,100)
	iterationNumber.pack(side=LEFT)

	iterationButton=Button(numberIterationFrame, text="select", command=selectIterationsNumber)
	iterationButton.pack()
	###Fin choix du nombre d'iterations

	###choix du critere de desagregation
	disaggregationCriterionFrame=Frame(principalFrame)
	disaggregationCriterionFrame.pack()

	disaggregationCriterion=StringVar()

	Label(disaggregationCriterionFrame,text="Disaggregation criterion (%) : ").pack(side=LEFT)

	criterion= Entry(disaggregationCriterionFrame, width=3, textvariable=disaggregationCriterion)
	criterion.insert(0,2)
	criterion.pack(side=LEFT)

	criterionButton=Button(disaggregationCriterionFrame, text="select", command=selectDisaggregationCriterion)
	criterionButton.pack()
	###Fin choix du nombre d'iterations

	###choix du critere de desagregation
	monteCarloFrame=Frame(principalFrame)
	monteCarloFrame.pack()

	correlatedMC = BooleanVar()
	nocorrelatedMC = BooleanVar()

	Checkbutton(monteCarloFrame, text="correlated Monte-Carlo", variable=correlatedMC).pack()
	Checkbutton(monteCarloFrame, text="nocorrelated Monte-Carlo", variable=nocorrelatedMC).pack()

	nocorrIntervalFrame=Frame(monteCarloFrame)
	nocorrIntervalFrame.pack()
	nocorrBegin=IntVar()
	nocorrBegin.set(0)
	nocorrEnd=IntVar()
	nocorrEnd.set(3)
	Label(nocorrIntervalFrame,text="interval des indices a calculer : ").pack(side=LEFT)
	Entry(nocorrIntervalFrame,width=4, textvariable=nocorrBegin).pack(side=LEFT)
	Label(nocorrIntervalFrame,text="->").pack(side=LEFT)
	Entry(nocorrIntervalFrame,width=4, textvariable=nocorrEnd).pack(side=LEFT)
	###Fin choix du nombre d'iterations

	###Informations
	informationsFrame=Frame(principalFrame,width=50, height=20)
	informationsFrame.pack()
	
	progress=IntVar()
	pb_hD = ttk.Progressbar(informationsFrame, length= 500, mode='determinate', variable=progress)

	runButton=Button(principalFrame,text="Run", command=calcul)
	runButton.pack(side=LEFT)
	cleanButton=Button(principalFrame,text="Clean", command=cleaningAll)
	cleanButton.pack(side=LEFT)

	fenetre.mainloop()#run the interface



