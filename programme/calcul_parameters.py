def calcul_parameters(UP_list, path, nb_categories):
	from numpy import loadtxt, log, sqrt, var, mean, transpose, matrix, abs, sign, zeros
	import os
	import warnings
	warnings.filterwarnings("ignore")
	
	sigma=zeros((len(UP_list),nb_categories))
	mu=zeros((len(UP_list),nb_categories))
	sgn=zeros((len(UP_list),nb_categories))
		
	up_calc=os.listdir(path)
	for up in range(len(UP_list)):
		if str(up)+".csv" in up_calc:
			try:
				data=loadtxt(open(os.path.join(path,str(up)+".csv"), "rb"), delimiter=",", dtype=float)
			except:
				print up
				raw_input()
			variance=var(data,0)
			E=mean(data,0)
			try:
				for cat in range(nb_categories):
					if E[cat+1]!=0 and variance[cat+1]!=0:
						s2=log(1+variance[cat+1]/(E[cat+1]*E[cat+1]))
						sigma[up,cat]=sqrt(s2)
						mu[up,cat]=log(abs(E[cat+1]))-s2/2
						sgn[up,cat]=sign(E[cat+1])
				"""
				for (v,e) in zip(variance,E):
					if e==0 or v==0:
						line_sigma.append(0)
						line_mu.append(0)
						line_sgn.append(0)
					else:
						s2=log(1+v/(e*e))
						line_sigma.append(sqrt(s2))
						line_mu.append(log(abs(e))-s2/2)
						line_sgn.append(sign(e))
			"""
			except:
				1

	return sigma, mu, sgn
