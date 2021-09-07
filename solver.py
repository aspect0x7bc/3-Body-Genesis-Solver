import numpy as np
import scipy as sci
from scipy.integrate import solve_ivp

'''
# @title - 'solves' three body problem for provided inital conditions (param hash)
# @author - @0xaspect
# @dev - calculates the position vectors of three equal mass bodies as they move in space from time 0 to 5 as defined by Newton's law of gravitation (no real units)
# @param hash - a string of 64 hex digits designed to come from a hashing function (keccak-256). gets equations initial values through 'bound' function
# @return - [r1, r2, r3, t, score]
#           r1,r2,r3: position vectors of the three bodies. r1[i] gives [x,y,z] of at time i
#           t: time steps between 0 and 5 generally t[i] - t[i+1] = 0.005 (max_step) but not always so length is variable
#           score: score the 'stableness' of a given solution by summing the average magnitude of the positon vectors for each time step (lower score -> more stable)
'''

def solve(hash):

    (m1, m2, m3) = (1, 1, 1)
    t_span = (0, 5)

    # Bound value between two points with a resolution of 16^-3 (since we are using 3 hex chars)
    # 000 gives this_min while fff gives this_max. 800 gives the midway point
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

    # diff eq solution to Newton's law of gravitation
    def derivs(t, w):
        r1=w[:3]
        r2=w[3:6]
        r3=w[6:9]
        v1=w[9:12]
        v2=w[12:15]
        v3=w[15:18]
        
        # normal vectors
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

    # solution - see scipy.integrate.solve_ivp
    sol = solve_ivp(derivs, t_span, state, max_step=0.005)

    # intigration error. raise up to api to handle
    # Im not sure what can be done to remedy this, if you know please lmk or make a pull request
    if not sol.success:
        raise ValueError(sol.message)

    r1=np.array([[x,y,z] for x,y,z in zip(sol.y[0], sol.y[1], sol.y[2])])
    r2=np.array([[x,y,z] for x,y,z in zip(sol.y[3], sol.y[4], sol.y[5])])
    r3=np.array([[x,y,z] for x,y,z in zip(sol.y[6], sol.y[7], sol.y[8])])

    # return r vecs relative to Center Of Mass
    rcom=(m1*r1+m2*r2+m3*r3)/(m1+m2+m3)
    r1com=r1-rcom
    r2com=r2-rcom
    r3com=r3-rcom
    t=list(sol.t)

    # calculate score - lower is better, more 'stable'
    # sum of the average magnitude of position vectors for each time step
    score = 0
    for i in range(len(t)):
        avg_magnitude = 0
        avg_magnitude += sci.linalg.norm(r1com[i])
        avg_magnitude += sci.linalg.norm(r2com[i])
        avg_magnitude += sci.linalg.norm(r3com[i])
        score += avg_magnitude / 3

    # finally get average of time step
    score = score / len(t)

    return (r1com.tolist(), r2com.tolist(), r3com.tolist(), t, score)