import math
import numpy as np
import matplotlib.pyplot as plt
import scipy as sp
from scipy.optimize import fsolve

'''
this class is currently for sizing a bipropellant coax swirl injector
functionality for other injector types may be added later.
the equations and derivations for the swirl injector sizing
can be found in the following paper.
"Design and Dynamics of Jet and Swirl Injectors" Vladimir Bazarov, Vigor Yang, Puneesh Puri
'''
class Injector:
    def __init__(self):

        #user input values
        # self.mdot1 = mdot1  # mass flow rate stage 1
        # self.mdot2 = mdot2  # mass flow rate stage 2
        # self.p_f1 = p_f1      # pressure of the preasure feed system befor injection
        # self.p_in1 = p_in1    # pressure after being injected to the swirler
        # self.p_c1 = p_c1      # pressure of chamber
        # self.p_f2 = p_f2      # pressure of the preasure feed system befor injection
        # self.p_in2 = p_in2    # pressure after being injected to the swirler
        # self.p_c2 = p_c2      # pressure of chamber        
        # self.alpha1 = alpha1  # spray cone angle
        # self.alpha2 = alpha2  # spray cone angle
        # self.n1 = n1          # number of tangential injection passages
        # self.n2 = n2          # number of tangential injection passages
        # self.rho1 = rho1      # density of fluid
        # self.rho2 = rho2      # density of fluid
        # self.nu1 = nu1        # kinematic viscosity
        # self.nu2 = nu2        # kinematic viscosity
        # self.l_in1 = l_in1    # 3-6, length of tangential passages
        # self.l_n1 = l_n1      # 0.5-2, length of nozzle
        # self.l_s1 = l_s1      # l_s>2, length of vortex chamber
        # self.l_in2 = l_in2    # 3-6, length of tangential passages
        # self.l_n2 = l_n2      # 0.5-2, length of nozzle
        # self.l_s2 = l_s2      # l_s>2, length of vortex chamber

        self.mu = None      # mass flow coefficient
        self.phi = None     # coefficient of passage fullness, or fractional area occupied by liquid in the nozzle
        self.h = None       # head
        self.v_sum = None   # total velocity
        self.v_un = None    
        self.v_an = None
        self.v_rn = None
        self.v_uk = None
        self.v_rk = None
        self.v_in = None
        self.r_mk = None
        self.r_mn = None
        self.R_in = None
        self.A = None

#step 1
    '''
Prescribe the spray cone angle based on the injector operating conditions
(usually between 90 and 120 deg, lower values may be used for special
cases). The geometric characteristic parameter A and the flow coefficient mu
are then determined from the plots in Fig. 32.
    '''
#alpha is gigen as an input
#with alpha angle chosen, values for phi, mu and A can be calculated
    def calc_phi_mu_A(self, alpha): #aplha needs to be in radians for this to work
        def funcPhiMu(z, alpha):
            phi = z[0]
            mu = z[1]
            F = np.empty((2))
            F[0] = np.tan(alpha) - np.sqrt(2*(1-phi)/phi) #eq 74
            F[1] = mu - phi*np.sqrt(phi/(2-phi)) #eq 62
            return F
        zGuess = np.array([0.8,0.8])
        #alpha = 60*np.pi/180 
        phi, mu = fsolve(funcPhiMu,zGuess, args=(alpha,))

        def funcA(A, phi, mu):
            return mu - 1/np.sqrt(A**2/(1-phi)+1/phi**2) #eq 61
        AGuess = 0.5
        A = fsolve(funcA, AGuess, args=(phi, mu,))
        return A, phi, mu

#step 2
#determine nozzle radius R_n
# this can be done with the calculated mu from step 1 and inpit values
# of mdot, rho, and deltaP
# the deltaP is the total pressure drop
    def calc_R_n(self, mdot, mu, rho, deltaP):
        R_n = 0.475*np.sqrt(mdot/(mu*np.sqrt(rho*deltaP))) #eq 103
        return R_n
#step 3
    '''
Specify the number of inlet passages (usually between two and four) and the
coefficient of injector opening, based on structural considerations. Then, the
radius of the inlet passage is obtained
    '''
# number of passages n is user input
# R_in is decided from structural considerations NOTE: learn more about this
# A and R_n are calculated from steps 1 and 2 respectivly
    def calc_r_in(self, R_in, R_n, n, A):
        r_in = np.sqrt(R_in*R_n/(n*A)) #eq 104
        return r_in
#step 4
# R_n, R_in, and r_in from steps 2 and 3
# l_in, l_n, l_s are user input, chosen from a select range shown below
# l_in = 3-6
# l_n = 0.5-2
# l_s > 2
# #NOTE: maybe add user input on this step so numbers can be changed through each iteration
    def calc_lengths(self, r_in, R_in, R_n, l_in, l_n, l_s):
        l_in = l_in*r_in
        l_n = l_n*R_n
        l_s = l_s*R_in
        R_s = R_in + r_in
        return l_in, l_n, l_s, R_s
#step 5
# find reynolds number in the inlet passages
# n and r_in are from previous steps
# mdot, rho, and nu are user input values
    def calc_Re(self, mdot, n, r_in, rho, nu):
        Re = 0.637*mdot/(np.sqrt(n)*r_in*rho*nu) #eq 101
        return Re
#step 6
# calculate A_eq and use that to get mu_eq and alpha_eq from the methods used in step 1
# R_in, R_n, n, r_in, Re are calculated from previous steps
    def calc_lam(self, Re):
        lam = 0.3164/(Re)**0.25 #eq 101
        return lam
    def calc_A_eq(self, R_in, R_n, n, r_in, lam):
        A_eq = R_in*R_n/(n*r_in**2+lam/2*R_in*(R_in-R_n)) #eq 100
        return A_eq
    def calc_phi_eq(self, A_eq):
        def funPhi(phi, A):
            return A - (1-phi)*np.sqrt(2)/(phi*np.sqrt(phi))#eq 92
        phiGuess = 0.5
        phi_eq = fsolve(funPhi, phiGuess, args=(A_eq,))
        return phi_eq
    def calc_mu_eq(self, phi): 
        mu = phi*np.sqrt(phi)/np.sqrt(2-phi) #eq 62
        return mu
    def calc_alpha_eq(self, phi): 
        alpha_eq = np.arctan(np.sqrt(2*(1-phi)/phi)) #eq 74
        return alpha_eq
#step 7
#Calculate the hydraulic-loss coefficient in the tangential passages
# first eps_in must be obtained
# this hydraulic loss coefficient is reltated to the inlet geometry of the inlet passages
# there are different equations for sharp edges, rounded, and angled orifice inlets
# figure 25 in the paper show these relations
# R_s, l_in, lam, and r_in are calculated from previous steps
    def calc_eps_in(self, R_s, l_in): 
        alpha = 90-180/np.pi*np.arctan(R_s/l_in)
        eps_in = -0.015*(alpha-30)+0.9 # linear equation from figure 25
        return eps_in
    def calc_eps(self, eps_in, lam, l_in, r_in):
        eps = eps_in + lam*l_in/(2*r_in) #eq 20
        return eps
#step 8
#Determine the actual flow coefficient
# mu_eq, eps, R_in, R_n, A are calculated from previous steps
#NOTE: check which A to use
    def calc_mu(self, mu_eq, eps, R_in, R_n, A):
        Rbar_in = R_in/R_n
        mu = mu_eq/np.sqrt(1+eps*mu_eq**2*A**2/Rbar_in**2) # eq 99
        return mu
#step 9
# Calculate the nozzle radius using the new approximation
# this step reuses the function from step 2 but with new value for mu

#step 10
# Calculate the geometric parameter A with the new value for R_n
# R_in, R_n, and r_in are calculated from previous steps
# n is user input
    def calc_A(self,R_in, R_n, n, r_in):
        A = R_in*R_n/(n*r_in**2) #eq 48
        return A

#step 11
# Repeat steps 1-10 until the calculated injector parameters converge.

    def calculate1(self, mdot, p_f, p_in, p_c, alpha, n, rho, nu, l_n_ratio, l_in_ratio, l_s_ratio):
        deltaP = p_f - p_c #NOTE: confirm this is correct
        print(f"input values: \nalpha = {alpha}\ndeltaP = {deltaP}\nl_in_ratio = {l_in_ratio}\nl_n_ratio = {l_n_ratio}\nl_s_ratio = {l_s_ratio}")
        print("calculated values:")
        A, phi, mu = self.calc_phi_mu_A(alpha)
        print('A = {}\nphi = {}\nmu = {}'.format(A, phi, mu))
        R_n = self.calc_R_n(mdot, mu, rho, deltaP)
        print(f'R_n = {R_n}')
        interationsCount = 0
        alphaOld = 0
        while abs(alpha-alphaOld)>0.001:
            interationsCount += 1
            print()
            print(f'iteration: {interationsCount}')
            alphaOld = alpha
            R_in = R_n*1.25 # consider making this a user input check for each iteration
            print(f'R_in = {R_in}')
            r_in = self.calc_r_in(R_in, R_n, n, A)
            print(f'r_in = {r_in}')
            l_in, l_n, l_s, R_s = self.calc_lengths(r_in, R_in, R_n, l_in_ratio, l_n_ratio, l_s_ratio)
            print('l_in = {}\nl_n = {}\nl_s = {}\nR_s = {}'.format(l_in, l_n, l_s, R_s))
            Re = self.calc_Re(mdot, n, r_in, rho, nu)
            print(f'Re = {Re}')
            lam = self.calc_lam(Re)
            print(f'lam = {lam}')
            A_eq = self.calc_A_eq(R_in, R_n, n, r_in, lam)
            print(f'A_eq = {A_eq}')
            phi_eq = self.calc_phi_eq(A_eq)
            print(f'phi_eq = {phi_eq}')
            mu_eq = self.calc_mu_eq(phi_eq)
            print(f'mu_eq = {mu_eq}')
            alpha_eq = self.calc_alpha_eq(phi_eq)
            print(f'alpha_eq = {alpha_eq}')
            eps_in = self.calc_eps_in(R_s, l_in)
            eps_in = 0.1
            print(f'eps_in = {eps_in}')
            eps = self.calc_eps(eps_in, lam, l_in, r_in)
            print(f'eps = {eps}')
            mu = self.calc_mu(mu_eq, eps, R_in, R_n, A)
            print(f'mu = {mu}')
            R_n = self.calc_R_n(mdot, mu, rho, deltaP)
            print(f'R_n = {R_n}')
            A = self.calc_A(R_in, R_n, n, r_in)
            print(f'A = {A}')
            phi = self.calc_phi_eq(A)
            print(f'phi_eq = {phi_eq}')
            mu = self.calc_mu_eq(phi)
            print(f'mu_eq = {mu_eq}')
            alpha = self.calc_alpha_eq(phi)
            print(f'alpha_eq = {alpha_eq}')


        self.mdot = mdot
        self.p_f = p_f
        self.p_in = p_in
        self.p_c = p_c
        self.alpha = alpha
        self.n = n
        self.rho = rho
        self.nu =  nu
        self.l_n = l_n
        self.l_in = l_in
        self.l_s = l_s
        self.R_in = R_in
        self.R_s = R_s
        self.R_n = R_n
        self.r_in = r_in
        self.l_in = l_in
        self.l_n = l_n
        self.l_s = l_s
        self.alpha = alpha_eq
        self.phi = phi
        self.mu = mu
        self.A = A
        self.eps = eps
        self.Re = Re
    
    '''
this calculates a monopropellant swirl element with a method that
uses experimental data to simplify the calculations
    '''
    def calculate2(self, alpha, l_n__R_n, A, mu_in, mdot, rho, n, R_in_ratio, p_f, p_c, l_in_ratio, l_n_ratio, l_s_ratio, lenghtUnits = 'in'):
        #step 1
        # alpha, l_n__D_n, A, mu_in are manually input values
        l_n_ratio = l_n__R_n*2
        #step 2
        # mdot, rho and deltaP are input values
        deltaP = p_f - p_c
        R_n = self.calc_R_n(mdot, mu_in, rho, deltaP)
        #step 3
        # n, R_in_ratio are input values
        R_in = R_n*R_in_ratio
        r_in = self.calc_r_in(R_in, R_n, n, A)
        #step 4
        Re_in = self.calc_Re(mdot, n, r_in, rho, nu)
        if Re_in < 10000:
            print(f'Re_in = {Re_in}\nRe_in must be larger than 10000\nchange input values to achive this')
            return None
        else:
            print(f'Re_in = {Re_in}')
        #step 5
        # l_in_ratio, l_n_ratio, l_s_ratio, rbar_m are input values
        l_in, l_n, l_s, R_s = self.calc_lengths(r_in, R_in, R_n, l_in_ratio, l_n_ratio, l_s_ratio)
        rbar_m = float(input(f"A = {A}\nRbar_in = {R_in/R_n}\nenter the corresponding rbar_m from figure 35:"))
        r_m = rbar_m*R_n
        if lenghtUnits == 'm':
            pass
        elif lenghtUnits == 'in':
            R_in = R_in * 39.37
            R_s = R_s * 39.37
            R_n = R_n * 39.37
            r_in = r_in * 39.37
            l_in = l_in * 39.37
            l_n = l_n * 39.37
            l_s = l_s * 39.37
        print(f'''
            R_in = {R_in} {lenghtUnits}\t radial location of tangential inlet passages
            R_s = {R_s} {lenghtUnits}\t radius of vortex chamber
            R_n = {R_n} {lenghtUnits}\t radius of nozzle
            r_in = {r_in} {lenghtUnits}\t radius of inlet passages
            l_in = {l_in} {lenghtUnits}\t lenth of tangential inlet passages
            l_n = {l_n} {lenghtUnits}\t length of nozzle
            l_s = {l_s} {lenghtUnits}\t length of vortex chamber
            alpha = {alpha}
            mu = {mu_in}
            A = {A}
            Re_in = {Re_in}
            deltaP = {deltaP}
        ''')

    def calc_mu2(self, mdot, R_n, rho, deltap):
        print('----------')
        print(f'mdot = {mdot}\nR_n = {R_n}\nrho = {rho}\ndeltap = {deltap}')
        print('----------')
        return mdot/(R_n)**2/np.sqrt(rho*deltap)

    def clac_l_mix(self, k_m, phi_1, phi_2, mu_1, mu_2, rho_1, rho_2, deltap_1, deltap_2, tau):
        l_mix = np.sqrt(2)*tau*((k_m*mu_2)/((k_m+1)*phi_2)*np.sqrt(deltap_2/rho_2) + (mu_1)/((k_m+1)*phi_1)*np.sqrt(deltap_1/rho_1))
        return l_mix
    '''
this method uses much the same procedure as the monopropellant element sizing except that it is ment for
designing two nested elements denoted as stage 1 being the inner element and stage 2 being the outer.
there is also an option for internal or external mixing which involve different calculations.
there are 2 calculations senerios which effect the sizing of the stage 2 element:
senerio 1 the wall of the stage 1 nozzle is within the gaseouse core of the stage 2 nozzle flow
senerio 2 the stage 1 nozzle is submerged and effecting the flow of the stage 2 nozzle
    '''
    #calculateBipropellant 1 uses manually inputed experimental data from graphs
    def calculateBipropellant1(self, mdot_1, mdot_2, deltap_1, deltap_2, alpha_1, alpha_2, n_1, n_2, rho_1, rho_2, nu_1, nu_2, l_n_ratio1, l_in_ratio1, l_s_ratio1, l_n_ratio2, l_in_ratio2, l_s_ratio2, del_w, deltar, tau, lenUnits = 'in', angleUnits = 'degrees'):
        # stage 1 sizing calculations
        print(f"input values: \nalpha_1 = {alpha_1}\nalpha_2 = {alpha_2}\ndeltap_1 = {deltap_1}\ndeltap_2 = {deltap_2}\nn_1 = {n_1}\nn_2 = {n_2}\nl_in_ratio = {l_in_ratio}\nl_n_ratio = {l_n_ratio}\nl_s_ratio = {l_s_ratio}")
        print("calculated values:")
        A_1, phi_1, mu_1 = self.calc_phi_mu_A(alpha_1)
        #print('A = {}\nphi = {}\nmu = {}'.format(A, phi, mu))
        R_n1 = self.calc_R_n(mdot_1, mu_1, rho_1, deltap_1)
        interationsCount = 0
        alphaOld1 = 0
        while abs(alpha_1-alphaOld1)>0.001:
            interationsCount += 1
            print()
            print(f'iteration: {interationsCount}')
            alphaOld1 = alpha_1
            R_in1 = R_n1*1.25 # consider making this a user input check for each iteration
            #print(f'R_in = {R_in}')
            r_in1 = self.calc_r_in(R_in1, R_n1, n_1, A_1)
            #print(f'r_in = {r_in}')
            l_in1, l_n1, l_s1, R_s1 = self.calc_lengths(r_in1, R_in1, R_n1, l_in_ratio1, l_n_ratio1, l_s_ratio1)
            #print('l_in = {}\nl_n = {}\nl_s = {}\nR_s = {}'.format(l_in, l_n, l_s, R_s))
            Re_1 = self.calc_Re(mdot_1, n_1, r_in1, rho_1, nu_1)
            #print(f'Re = {Re}')
            lam_1 = self.calc_lam(Re_1)
            #print(f'lam = {lam}')
            A_eq1 = self.calc_A_eq(R_in1, R_n1, n_1, r_in1, lam_1)
            #print(f'A_eq = {A_eq}')
            phi_eq1 = self.calc_phi_eq(A_eq1)
            #print(f'phi_eq = {phi_eq}')
            mu_eq1 = self.calc_mu_eq(phi_eq1)
            #print(f'mu_eq = {mu_eq}')
            alpha_eq1 = self.calc_alpha_eq(phi_eq1)
            #print(f'alpha_eq = {alpha_eq}')
            #eps_in = self.calc_eps_in(R_s, l_in)
            eps_in1 = 0.2
            #print(f'eps_in = {eps_in}')
            eps_1 = self.calc_eps(eps_in1, lam_1, l_in1, r_in1)
            #print(f'eps = {eps}')
            mu_1 = self.calc_mu(mu_eq1, eps_1, R_in1, R_n1, A_1)
            #print(f'mu = {mu}')
            R_n1 = self.calc_R_n(mdot_1, mu_1, rho_1, deltap_1)
            #print(f'R_n = {R_n}')
            A_1 = self.calc_A(R_in1, R_n1, n_1, r_in1)
            #print(f'A = {A}')
            phi_1 = self.calc_phi_eq(A_1)
            #print(f'phi_eq = {phi_eq}')
            mu_1 = self.calc_mu_eq(phi_1)
            #print(f'mu_eq = {mu_eq}')
            alpha_1 = self.calc_alpha_eq(phi_1)
            #print(f'alpha_eq = {alpha_eq}')
        #stage 2 calculations
        A_2, phi_2, mu_2 = self.calc_phi_mu_A(alpha_2)
        print('A_2 = {}\nphi_2 = {}\nmu_2 = {}'.format(A_2, phi_2, mu_2))
        #R_n2 = R_n1+del_w+deltar+r_mn2 #first aproximation of R_n2
        #r_mn2 = np.sqrt(1-phi_2)*R_n2
        #print(f'R_n = {R_n}')
        R_n2 = 0 #(R_n1+del_w+deltar)/np.sqrt(1-phi_2)
        oldR_n2 = 1
        interationsCount2 = 0
        while abs(R_n2-oldR_n2) > 0.0001:
            oldR_n2 = R_n2
            print(f'oldR_n2 = {oldR_n2}')
            interationsCount2 += 1
            print()
            print(f'iteration: {interationsCount2}')
            R_n2 = (R_n1+del_w+deltar)/np.sqrt(1-phi_2)
            print(f'R_n2 = {R_n2}')
            mu_2 = self.calc_mu2(mdot_2, R_n2, rho_2, deltap_2)
            print(f'mu_2 = {mu_2}')
            def funcphi(phi, mu):
                return mu - phi*np.sqrt(phi/(2-phi))
            phiGuess = 0.8
            phi_2 = fsolve(funcphi, phiGuess, args=(mu_2,))
            print(f'phi_2 = {phi_2}')
            print(f'abs(R_n2-oldR_n2) = {abs(R_n2-oldR_n2)}')
        r_mn2 = np.sqrt(1-phi_2)*R_n2
        def funcA(A, phi):
            return A - (1-phi)*np.sqrt(2)/(phi*np.sqrt(phi)) 
        AGuess = 0.5
        A_2 = fsolve(funcA, AGuess, args=(phi_2))
        R_in2 = R_n2 * 1.25 #R_n2_ratio
        print(f'R_in2 = {R_in2}\nR_n2 = {R_n2}\nn_2 = {n_2}\nA_2 = {A_2}')
        r_in2 = self.calc_r_in(R_in2, R_n2, n_2, A_2) #np.sqrt(R_n2*R_in2/(n_2*A_2))
        print(f'mdot_2 = {mdot_2}\nn_2 = {n_2}\nr_in2 = {r_in2}\nrho_2 = {rho_2}\nnu_2 = {nu_2}\n')
        Re_in2 = self.calc_Re(mdot_2, n_2, r_in2, rho_2, nu_2)
        if Re_in2 < 10000:
            print(f'Re_in = {Re_in2}\nRe_in must be larger than 10000\nchange input values to achive this')
        else:
            print(f'Re_in = {Re_in2}')
        alpha = alpha_2-17.5*np.pi/180
        k_m = 1/(mdot_1/mdot_2)
        l_mix = self.clac_l_mix(k_m, phi_1, phi_2, mu_1, mu_2, rho_1, rho_2, deltap_1, deltap_2, tau)
        l_in2, l_n2, l_s2, R_s2 = self.calc_lengths(r_in2, R_in2, R_n2, l_in_ratio2, l_n_ratio2, l_s_ratio2)
        deltal_n2 = (r_mn2 - R_n1)/np.tan(alpha_1)
        new_l_n2 = l_mix + deltal_n2
        if lenUnits == 'in': #NOTE: add length units conversion
            R_n1 *= 39.37
            R_n2 *= 39.37
            R_in1 *= 39.37
            R_in2 *= 39.37
            r_in1 *= 39.37
            r_in2 *= 39.37
            l_in1 *= 39.37
            l_in2 *= 39.37
            l_n1 *= 39.37
            l_n2 *= 39.37
            l_s1 *= 39.37
            l_s2 *= 39.37
            R_s1 *= 39.37
            R_s2 *= 39.37
            l_mix *= 39.37
            new_l_n2 *= 39.37
            del_w *= 39.37
            deltar *= 39.37
        if angleUnits == 'degrees':
            alpha *= 180/np.pi
            alpha_1 *= 180/np.pi
            alpha_2 *= 180/np.pi
        
        print(f'''
            mdot_1 = {mdot_1} kg/s
            mdot_2 = {mdot_2} kg/s
            deltap_1 = {deltap_1} Pa
            deltap_2 = {deltap_2} Pa
            alpha_1 = {alpha_1} {angleUnits}
            alpha_2 = {alpha_2} {angleUnits}
            n_1 = {n_1}
            n_2 = {n_2}
            rho_1 = {rho_1} kg/m^3
            rho_2 = {rho_2} kg/m^3
            nu_1 = {nu_1} m^2/s
            nu_2 = {nu_2} m^2/s
            Re_1 = {Re_1}
            Re_2 = {Re_in2}
            l_n_ratio1 = {l_n_ratio1}
            l_in_ratio1 = {l_in_ratio1}
            l_s_ratio1 = {l_s_ratio1}
            l_n_ratio2 = {l_n_ratio2}
            l_in_ratio2 = {l_in_ratio2}
            l_s_ratio2 = {l_s_ratio2}
            del_w = {del_w} {lenUnits}
            deltar = {deltar} {lenUnits}
            tau = {tau} s
            A_1 = {A_1}
            A_2 = {A_2}
            mu_1 = {mu_1}
            mu_2 = {mu_2}
            phi_1 = {phi_1}
            phi_2 = {phi_2}
            R_n1 = {R_n1} {lenUnits}
            R_n2 = {R_n2} {lenUnits}
            R_in1 = {R_in1} {lenUnits}
            R_in2 = {R_in2} {lenUnits}
            r_in1 = {r_in1} {lenUnits}
            r_in2 = {r_in2} {lenUnits}
            l_in1 = {l_in1} {lenUnits}
            l_in2 = {l_in2} {lenUnits}
            l_n1 = {l_n1} {lenUnits}
            l_n2 = {l_n2} {lenUnits}
            l_s1 = {l_s1} {lenUnits}
            l_s2 = {l_s2} {lenUnits}
            R_s1 = {R_s1} {lenUnits}
            R_s2 = {R_s2} {lenUnits}
            l_mix = {l_mix} {lenUnits}
            new_l_n2 = {new_l_n2} {lenUnits}
            alpha = {alpha} {angleUnits}
            k_m = {k_m}
        ''')

        # step 1
        '''
1) Prescribe the spray cone angles 2alpha_2 and 2alpha_1, according to the empirical
condition 2alpha_1 — 2alpha_2 = 10 to 15 deg based on injector operating conditions.
With these values and the correlation given in Fig. 34a, find the geometric characteristic parameters, A1 and A2.
The flow coefficients of stages 1 and 2, mu_1 and mu_2, are then determined from Fig. 34b
        '''

        # step 2
        '''
2) Calculate the nozzle radii R_n1 and R_n2 from Eq. (103), and determine the
tangential-entry radii r_in1 and r_in2 from Eq. (104).
        '''

        # step 3
        '''
3) Determine the Reynolds numbers Re_in1 and Re_in2 using Eq. (101). The
design is completed if Re_in > 10^4, and the injector dimensions and flow
parameters are calculated.
        '''
        # stage 2 sizing calculations

        #mixing element sizing calculations
        #calculateBipropellant 2 uses calculated data from methods used in monopropellant calculator
    def calculateBipropellant2(self, senerio):
        #stage 1 calculations
        #step 1 
        '''
        1) the gas-column radius of stage 2 should exceed the external radius of the
        nozzle of stage 1, with rm2 — rm\ = 0.2-0.3 mm
        '''
        #step 2
        '''
        2) the spray cone angle of stage 1 should be such that the propellant arrives at
        the mixer wall 2-3 mm downstream of the tangential entries of stage 2.
        '''
        deltap_i1 = None
        deltap_i2 = None
        mdot_i1 = None
        mdot_i2 = None
        Rbar_in1 = None
        Rbar_in2 = None
        lbar_n1 = None
        lbar_n2 = None
        n_1 = None
        n_2 = None
        #step 3
        '''

        '''

        #stage 2 calculations
        if senerio == 0:
            pass
        else:
            pass
#--------------------------------------------------------------------------------------
    def swirlgraphs(self):
        def y(x, A):
            return 1 / np.sqrt(A**2/(1-x) + 1/x**2)

        # Define the range of x values to plot
        x = np.linspace(0.01, 0.99, 1000)

        # Define the values of A to plot
        A_values = [2.0, 0.8, 0.4, 0.2]

        # Create a figure and axes object
        fig, ax = plt.subplots()

        # Plot the function for each value of A
        for A in A_values:
            ax.plot(x, y(x, A), label=f"A={A}")
        ax.plot(x, x*np.sqrt(x/(2-x)), label=f"ideal")

        # Set the title and axis labels
        ax.set_title("Graph of y = 1/(A^2/(1-x)+1/x^2)")
        ax.set_xlabel("x")
        ax.set_ylabel("y")

        # Add a legend and gridlines
        ax.legend()
        ax.grid()

        # Show the plot
        plt.show()
    def calc1variablesDisplay(self, lenghtUnits = 'in'):
        if lenghtUnits == 'm':
            R_in = self.R_in
            R_s = self.R_s
            R_n = self.R_n
            r_in = self.r_in
            l_in = self.l_in
            l_n = self.l_n
            l_s = self.l_s
        elif lenghtUnits == 'in':
            R_in = self.R_in * 39.37
            R_s = self.R_s * 39.37
            R_n = self.R_n * 39.37
            r_in = self.r_in * 39.37
            l_in = self.l_in * 39.37
            l_n = self.l_n * 39.37
            l_s = self.l_s * 39.37
        print(f'''
            R_in = {R_in} {lenghtUnits}\t radial location of tangential inlet passages
            R_s = {R_s} {lenghtUnits}\t radius of vortex chamber
            R_n = {R_n} {lenghtUnits}\t radius of nozzle
            r_in = {r_in} {lenghtUnits}\t radius of inlet passages
            l_in = {l_in} {lenghtUnits}\t lenth of tangential inlet passages
            l_n = {l_n} {lenghtUnits}\t length of nozzle
            l_s = {l_s} {lenghtUnits}\t length of vortex chamber
            alpha = {self.alpha}
            phi = {self.phi}
            mu = {self.mu}
            A = {self.A}
            eps = {self.eps}
            Re = {self.Re}
        ''')

    def __str__(self):
        return '''
            R_in = {} m radial location of tangential inlet passages
            R_s = {} m radius of vortex chamber
            R_n = {} m radius of nozzle
            r_in = {} m radius of inlet passages
            l_in = {} m lenth of tangential inlet passages
            l_n = {} m length of nozzle
            l_s = {} m length of vortex chamber
            alpha = {}
            phi = {}
            mu = {}
            A = {}        
            eps = {}
            Re = {}
        '''.format(
            self.R_in,
            self.R_s,
            self.R_n,
            self.r_in,
            self.l_in,
            self.l_n,
            self.l_s,
            self.alpha,
            self.phi,
            self.mu,
            self.A,
            self.eps,
            self.Re
        )

if __name__ == "__main__": #test values
    mdot_1 = 0.3/6/2 #0.7/6       #mass flow of stage 1 of one injection element
    mdot_2 = 0.7/6/2 #0.3/6       #mass flow of stage 2 of one injection element
    #pressures in pascals
    p_f = 24*10**5
    p_in = 23*10**5 # not currently being used
    p_c = 20*10**5
    alpha = 59.5*np.pi/180 #in radians


    n = 3
    l_in_ratio = 4.5   # l_in = 3-6
    l_n_ratio = 1    # l_n = 0.5-2
    l_s_ratio = 3     # l_s > 2
    rho = 997   #in kg/m^3
    nu = 0.6*10**(-6) #in m^2/s

    my_swirl_injector = Injector()
    my_swirl_injector.calculate1(mdot_1, p_f, p_in, p_c, alpha, n, rho, nu, l_n_ratio, l_in_ratio, l_s_ratio)
    print("------------------------------------")
    my_swirl_injector.calc1variablesDisplay()
    print("------------------------------------")
    alpha = 50
    l_n__R_n = 0.5
    A = 3.3
    mu_in = 0.18
    R_in_ratio = 1.25
    #my_swirl_injector.calculate2(alpha, l_n__R_n, A, mu_in, mdot_1, rho, n, R_in_ratio, p_f, p_c, l_in_ratio, l_n_ratio, l_s_ratio)
    deltap_1 = 4*10**5
    deltap_2 = 4*10**5
    alpha_1 = 60*np.pi/180
    alpha_2 = 60*np.pi/180
    n_1 = 6
    n_2 = 6
    rho_1 = 997#1141
    rho_2 = 997#800
    nu_1 = 1*10**(-6)#0.1*10**(-6) #in m^2/s
    nu_2 = 1*10**(-6)#0.2*10**(-6)#2.7*10**(-6) #in m^2/s
    l_n_ratio1 = 1
    l_in_ratio1 = 4.5
    l_s_ratio1 = 3
    l_n_ratio2 = 1
    l_in_ratio2 = 4.5
    l_s_ratio2 = 3
    del_w = 0.0008
    deltar = 0.0003
    tau = 0.2/1000
    my_swirl_injector.calculateBipropellant1(mdot_1, mdot_2, deltap_1, deltap_2, alpha_1, alpha_2, n_1, n_2, rho_1, rho_2, nu_1, nu_2, l_n_ratio1, l_in_ratio1, l_s_ratio1, l_n_ratio2, l_in_ratio2, l_s_ratio2, del_w, deltar, tau)