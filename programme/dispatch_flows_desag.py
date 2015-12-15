def dispatch_flows_desag(UP, UP_list, EF_list,all_flow, A, B, uncertainty_info, 
                    EF_unit, unit_converter, infrastructure_rescale, UP_meta_info,UP_list_desag_1):
	from treat_elementary_flow_info_desag import treat_elementary_flow_info_desag
	from treat_economic_flow_info_desag import treat_economic_flow_info_desag
    
	UP_name=UP_list[UP['UP_number']]
	UP_scaling_factor = UP_meta_info[UP_name]['scaling factor'] #just a shortcut
	if UP_meta_info[UP_name]['Infrastructure'] == 'Yes':
		UP_scaling_factor = UP_scaling_factor * infrastructure_rescale #infrastructures are rescaled to improve precision
	unit = UP_meta_info[UP_name]['unit']
	UP_number = UP['instance_ID']#UP_list.index(UP_name)##########
	A[UP_number] = {}##########
	B[UP_number] = {}##########
	uncertainty_info['technology'][UP_number] = {}
	uncertainty_info['intervention'][UP_number] = {}
    
	#the markers will point to elementary or economic flows
	elementary_flow_markers = ['Resources', 'Emissions to air', 'Emissions to water', 
                               'Emissions to soil', 'Non material emissions']
	economic_flow_markers = ['Avoided products', 'Materials/fuels', 'Electricity/heat', 
                             'Final waste flows', 'Waste to treatment']
    #those economic flow markers lead to negative coefficient in the technology matrix
	negative_markers = ['Materials/fuels', 'Electricity/heat', 'Final waste flows', 
					'Waste to treatment', 'Separated waste']
   
	for total_flow in all_flow[UP['UP_number']]:
		marker=total_flow['marker']
		if economic_flow_markers.count(marker): #if the flows are economic
			if negative_markers.count(marker): #fetching the sign of the coefficient
				sign = -1.0
			else:
				sign = 1.0
			#the information about the diagonal element has to be stored here, when the column is being filled
			uncertainty_info['technology'][UP_number][UP_number] = {}
			uncertainty_info['technology'][UP_number][UP_number]['distribution'] = 'NA'
			uncertainty_info['technology'][UP_number][UP_number]['spread1'] = 'NA'
			uncertainty_info['technology'][UP_number][UP_number]['spread2'] = 'NA'
			uncertainty_info['technology'][UP_number][UP_number]['spread3'] = 'NA'
			A[UP_number][UP_number] = 1.0
			#for each economic flow, the value, position in matrix and uncertainty info has to be put at the right place
			for flow in total_flow['flow']:
				UP_list, A, uncertainty_info = treat_economic_flow_info_desag(flow, UP, UP_number, UP_list, sign, A, 
                                                              UP_scaling_factor, unit_converter, marker, uncertainty_info, 
                                                              infrastructure_rescale, UP_meta_info,UP_list_desag_1)
		else: #if they are not economic flows, they an elementary flows
			#the name of the compartment depends on the marker
			if marker == 'Resources':
				compartment = 'Resources'
			elif marker == 'Emissions to air':
				compartment = 'Air'
			elif marker == 'Emissions to water':
				compartment = 'Water'
			elif marker == 'Emissions to soil':
				compartment = 'Soil'
			else:
				compartment = 'Non material emissions'
			#for each elementary flow, the value, position in matrix and uncertainty info has to be put at the right place
			for flow in total_flow['flow']:
				EF_list, B, uncertainty_info, EF_unit = treat_elementary_flow_info_desag(flow, UP_number, EF_list, B, 
                                                                UP_scaling_factor, unit_converter, compartment, uncertainty_info, EF_unit, UP_list)
    
	return UP_list, EF_list, A, B, uncertainty_info, EF_unit
