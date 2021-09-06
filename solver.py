import numpy as np
import scipy as sci
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

'''
#
#
#
#
#
'''

def solve(hash):

    (m1, m2, m3) = (1, 1, 1)
    t_span = (0, 5)

    '''
    Bound value between two points with a resolution of 16^-3 (since we are using 3 hex chars)
    000 gives this_min while fff gives this_max. 800 gives the midway point
    '''
    def bound(value, this_min, this_max):
        this_range = this_max - this_min
        big_step = this_range / 16.0
        little_step = big_step / 16.0
        tiny_step = little_step / 15.0
        big = int(value[0], 16) * big_step
        little = int(value[1], 16) * little_step
        tiny = int(value[2], 16) * tiny_step

        return big + little + tiny + this_min

    ivs = [] # array used for initial values for integration
    for x in range(18):

        # positons (x1, y1, z1, x2, y2, z2, x3, y3, z3)
        if x < 9:
            # slice list to give 3 values
            ivs.append(bound(hash[x*3:x*3+3], -0.75, 0.75))

        # velocities (vx1, vy1, vz1, vx2, ...)
        else:
            ivs.append(bound(hash[x*3:x*3+3], -0.05, 0.05))

    def derivs(t, w):
        r1=w[:3]
        r2=w[3:6]
        r3=w[6:9]
        v1=w[9:12]
        v2=w[12:15]
        v3=w[15:18]
        
        # normal vectorsS
        r12=sci.linalg.norm(r2-r1)
        r13=sci.linalg.norm(r3-r1)
        r23=sci.linalg.norm(r3-r2)
        
        dv1bydt=m2*(r2-r1)/r12**3+m3*(r3-r1)/r13**3
        dv2bydt=m1*(r1-r2)/r12**3+m3*(r3-r2)/r23**3
        dv3bydt=m1*(r1-r3)/r13**3+m2*(r2-r3)/r23**3
        dr1bydt=v1
        dr2bydt=v2
        dr3bydt=v3
        
        r12_derivs=np.concatenate((dr1bydt,dr2bydt))
        r_derivs=np.concatenate((r12_derivs,dr3bydt))
        v12_derivs=np.concatenate((dv1bydt,dv2bydt))
        v_derivs=np.concatenate((v12_derivs,dv3bydt))
        derivs=np.concatenate((r_derivs,v_derivs))
        return derivs

    state = np.array(ivs)
    state = state.flatten()

    sol = solve_ivp(derivs, t_span, state, max_step=0.005)

    # TODO Stuff...
    if not sol.success:
        raise ValueError(sol.message)

    r1=np.array([[x,y,z] for x,y,z in zip(sol.y[0], sol.y[1], sol.y[2])])
    r2=np.array([[x,y,z] for x,y,z in zip(sol.y[3], sol.y[4], sol.y[5])])
    r3=np.array([[x,y,z] for x,y,z in zip(sol.y[6], sol.y[7], sol.y[8])])

    rcom=(m1*r1+m2*r2+m3*r3)/(m1+m2+m3)
    r1com=r1-rcom
    r2com=r2-rcom
    r3com=r3-rcom
    t=list(sol.t)

    save_svg = False
    if(save_svg):
        fig = plt.figure(figsize=(10, 10))
        ax = fig.add_subplot(autoscale_on=True)
        ax.set_aspect('equal')

        fig.patch.set_facecolor('black')
        plt.axis('off')

        #Plot the orbits
        ax.plot(r1com[:,0],r1com[:,1],color="white")
        ax.plot(r2com[:,0],r2com[:,1],color="white")
        ax.plot(r3com[:,0],r3com[:,1],color="white")
        plt.axis('off')
        plt.savefig("test.svg")
        plt.show()


    return (r1com.tolist(), r2com.tolist(), r3com.tolist(), t)