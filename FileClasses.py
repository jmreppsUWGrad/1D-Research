
# -*- coding: utf-8 -*-
"""
######################################################
#             1D Heat Conduction Solver              #
#              Created by J. Mark Epps               #
#          Part of Masters Thesis at UW 2018-2020    #
######################################################

This file contains classes for reading and writing files in proper format:
    -write input file with domain and solver settings
    -read input file as input to solver

"""

# Dictionaries containing expected input file data; organized by type

keys_Settings=['MPI_Processes', 'Length','Nodes_x','k','Cp','rho','Darcy_mu', \
               'Particle_diam','Porosity', 'gas_constant', 'pore_gas']

keys_mesh=['bias_type_x','bias_size_x']

keys_Sources=['Source_Uniform','Source_Kim','Ea','A0','dH', 'Ignition']

keys_Species=['Species','Specie_IC']

keys_Time_adv=['Fo','dt','total_time_steps', 'total_time','Restart',\
               'Time_Scheme','Convergence','Max_iterations','Number_Data_Output']

keys_BCs=     ['bc_left_E','bc_right_E',\
              'bc_left_rad','bc_right_rad',\
              'bc_left_P','bc_right_P',\
              'bc_left_mass','bc_right_mass']


newline_check='\n' # This should be \n for Windows, \r for Ubuntu

import string as st

class FileOut():
    def __init__(self, filename, isBin):
        self.name=filename
        if isBin:
            write_type='wb'
        else:
            write_type='w'
        self.fout=open(filename+'.txt', write_type)
    
    # Write a single string with \n at end
    def Write_single_line(self, string):
        self.fout.write(string)
        self.fout.write('\n')
    
    # Header with information about file
    def header_cond(self, title='Run'):
        self.Write_single_line('######################################################')
        self.Write_single_line('#             1D Heat Conduction Solver              #')
        self.Write_single_line('#              Created by J. Mark Epps               #')
        self.Write_single_line('#          Part of Masters Thesis at UW 2018-2020    #')
        self.Write_single_line('######################################################\n')
        self.Write_single_line('############### '+title+' FILE #########################')
        self.Write_single_line('##########'+self.name+'##################\n')
    
    def input_writer_cond(self, settings, Sources, Species, BCs):
        self.Write_single_line('Settings:')
        for i in keys_Settings:
            try:
                self.fout.write(i)
                self.fout.write(':')
                self.Write_single_line(str(settings[i]))
            except:
                continue
#            self.fout.write('\n')
        
        self.Write_single_line('\nMeshing details:')
        for i in keys_mesh:
            try:
                self.fout.write(i)
                self.fout.write(':')
                self.Write_single_line(str(settings[i]))
    #            self.fout.write('\n')
            except:
                continue
        
        if bool(Species):
            self.Write_single_line('\nSpecies info:')
            for i in keys_Species:
                self.fout.write(i)
                self.fout.write(':')
                for j in range(len(Species[i])):
                    self.fout.write(str(Species[i][j]))
                    if j==len(Species[i])-1:
                        self.fout.write('\n')
                    else:
                        self.fout.write(',')
            
        self.Write_single_line('\nSource Terms:')
        for i in keys_Sources:
            try:
                self.fout.write(i)
                self.fout.write(':')
                self.Write_single_line(str(Sources[i]))
            except:
                continue
            
        self.Write_single_line('\nTime advancement:')
        for i in keys_Time_adv:
            try:
                self.fout.write(i)
                self.fout.write(':')
                self.Write_single_line(str(settings[i]))
            except:
                continue
        self.fout.write('Output_directory')
        self.fout.write(':')
        self.Write_single_line(str(settings['Output_directory']))
            
        self.Write_single_line('\nBoundary conditions:')
        for i in keys_BCs:
            # User readable BC format
            self.fout.write('#')
            self.fout.write(i)
            self.fout.write(':')
            self.Write_single_line(str(BCs[i]))
            # Input file readable format
            self.fout.write(i)
            self.fout.write(':')
            if st.find(i,'rad')>=0:
                if BCs[i]=='None':
                    self.Write_single_line('None')
                else:
                    self.Write_single_line(str(BCs[i][0])+','+str(BCs[i][1]))
            else:
                for j in range(len(BCs[i])/3):
                    self.fout.write(BCs[i][3*j]+',')
                    if BCs[i][3*j]=='C':
                        self.fout.write(str(BCs[i][1+3*j][0])+',')
                        self.fout.write(str(BCs[i][1+3*j][1])+',')
                    else:
                        self.fout.write(str(BCs[i][1+3*j])+',')
                    self.fout.write(str(BCs[i][2+3*j][0])+',')
                    self.fout.write(str(BCs[i][2+3*j][1]))
                    if len(BCs[i])/3-j!=1:
                        self.fout.write(',')
                    else:
                        self.fout.write('\n')
            
#        self.fout.write('\nInitial conditions:\n')
#        self.Write_single_line('T')
#        for i in range(len(T[:,0])):
#            self.Write_single_line(str(T[i,:]))
        
        self.fout.write('\n')
        
    def close(self):
        self.fout.close()
        
class FileIn():
    def __init__(self, filename, isBin):
        self.name=filename
        if isBin:
            read_type='rb'
        else:
            read_type='r'
        self.fin=open(filename, read_type)
        
    def Read_Input(self, settings, Sources, Species, BCs):
        for line in self.fin:
            if st.find(line, ':')>0 and st.find(line, '#')!=0:
                line=st.split(line, ':')
                # Domain settings
                if line[0] in keys_Settings:
                    if line[0]=='Nodes_x':
                        settings[line[0]]=int(line[1])
                    elif st.find(line[1], 'None')>=0 or st.find(line[1], ',')>=0\
                        or line[0]=='Domain' or st.find(line[1], 'spec')>=0 \
                        or line[0]=='pore_gas':
                        settings[line[0]]=st.split(line[1], newline_check)[0]
                    else:
                        settings[line[0]]=float(line[1])
                # Mesh settings
                elif line[0] in keys_mesh:
                    if st.find(line[0], 'type')>=0:
                        settings[line[0]]=st.split(line[1], newline_check)[0]
                    else:
                        settings[line[0]]=float(line[1])
                
                # Source term info
                elif line[0] in keys_Sources:
                    if st.find(line[1], 'None')>=0 or st.find(line[1], 'True')>=0\
                        or st.find(line[1], 'eta')>=0 or st.find(line[1], 'Temp')>=0\
                        or st.find(line[1], 'rho')>=0 or st.find(line[1], 'vol')>=0:
                        Sources[line[0]]=st.split(line[1], newline_check)[0]
                    else:
                        Sources[line[0]]=float(line[1])
                # Species info
                elif line[0] in keys_Species:
                    if line[0]=='Species':
                        Species[line[0]]=st.split(st.split(line[1], newline_check)[0], ',')
                        Species['keys']=Species[line[0]]
                    else:
                        Species[line[0]]=st.split(st.split(line[1], newline_check)[0], ',')
                        for i in range(len(Species[line[0]])):
                            Species[line[0]][i]=float(Species[line[0]][i])
                            
                # Time advancement details
                elif line[0] in keys_Time_adv:
                    if line[0]=='Time_Scheme' or st.find(line[1], 'None')>=0 \
                        or line[0]=='Restart':
                        settings[line[0]]=st.split(line[1], newline_check)[0]
                    elif line[0]=='total_time_steps' or line[0]=='Max_iterations'\
                        or line[0]=='Number_Data_Output':
                        settings[line[0]]=int(line[1])
                    elif line[0]=='Output_directory':
                        settings[line[0]]=line[1]+':'+st.split(line[2], newline_check)[0]
                    else:
                        settings[line[0]]=float(line[1])
                # Boundary conditions (all equations)
                elif line[0] in keys_BCs:
                    BC_info=st.split(line[1], ',')
                    BCs[line[0]]=[]
                    # Radiation BCs
                    if st.find(line[0], 'rad')>=0:
                        try:
                            BCs[line[0]]=[float(BC_info[0])]
                            BCs[line[0]]+=[float(BC_info[1])]
                        except:
                            BCs[line[0]]=st.split(BC_info[0], newline_check)[0]
                        del BC_info[0]
                    # All other BCs
                    i=0
                    while len(BC_info)>1:
                        BCs[line[0]]+=[BC_info[0]]
                        del BC_info[0]
                        # Constant value/flux of variable BCs
                        if BCs[line[0]][3*i]=='T' or BCs[line[0]][3*i]=='F'\
                            or BCs[line[0]][3*i]=='grad':
                            # Value into a float
                            BCs[line[0]]+=[float(BC_info[0])]
                            del BC_info[0]
                            BCs[line[0]]+=[(int(BC_info[0]),int(BC_info[1]))]
                            del BC_info[1], BC_info[0]
                        # Convective BC
                        else:
                            BCs[line[0]]+=[(float(BC_info[0]),float(BC_info[1]))]
                            del BC_info[1], BC_info[0]
                            BCs[line[0]]+=[(int(BC_info[0]),int(BC_info[1]))]
                            del BC_info[1], BC_info[0]
                        
                        i+=1
                    
        self.fin.close()