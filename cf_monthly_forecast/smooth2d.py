import numpy as np

def box_smooth_2D(field,n_ih,n_jh,lat_wgt=True,latitude=None):
    """
    Smooth a 2d field w/ dimensions (i,j) by applying a simple box filter (2d-equivalent to a running-mean)
    assumes cyclic j-coordinate (e.g., longitude for global data)
    note: n_ih = 1, n_jh = 1 will create averages of the central points and the 8 points around each 
    INPUT:
        field       : (numpy.array) with 2 dimensions (i,j)
        n_ih        : (int) number of grid points to take into account in positive & negative i-direction of the central point
        n_jh        : (int) number of grid points to take into account in positive & negative j-direction of the central point
        lat_wgt     : (boolean) whether to apply latitude weights in i-direction or not; if True, need to define latitude
        latitude    : (numpy.array) of length field.shape[0] (length of i-dimension) with latitudes used for weighting
    """
    
    if lat_wgt:
        assert latitude is not None, 'need to specify latitude vector of length N_i to apply latitude weighting'

    N_i,N_j = field.shape

    # pad the field in j direction (longitude):
    field_padded = np.concatenate([field[:,N_j-n_jh:],field,field[:,:n_jh]],axis=1)

    N_jp = field_padded.shape[1]

    box_kernel = np.ones([n_ih*2+1,n_jh*2+1]) # un-normalized kernel
    # use a copy of the original and overwrite, note that this means that edge points will keep un-smoothed values!
    smooth_field = field.copy()
    for i in range(N_i):
        for j in range(N_jp):
            if (i > n_ih) and (j > n_jh) and (i < N_i-n_ih-1) and (j < N_jp-n_jh-1):
                if lat_wgt:
                    lat_weight = np.cos(latitude[i-n_ih:i+n_ih+1]/180*np.pi)
                    wgts = lat_weight * box_kernel
                else:
                    wgts = box_kernel
                smooth_field[i,j-n_jh] = (wgts*field_padded[i-n_ih:i+n_ih+1,j-n_jh:j+n_jh+1]).sum()/wgts.sum()
    return smooth_field