#
# Collective Knowledge (individual environment - setup)
#
# See CK LICENSE.txt for licensing details
# See CK COPYRIGHT.txt for copyright details
#
# Developer: Grigori Fursin, Grigori.Fursin@cTuning.org, http://fursin.net
#

import os

##############################################################################
# get version from path

def version_cmd(i):

    hosd=i['host_os_dict']
    tosd=i['target_os_dict']

    win=hosd.get('windows_base','')

    ck=i['ck_kernel']

    fp=i['full_path']

    ver=''

    p0=os.path.basename(fp)
    p1=os.path.dirname(fp)

    px=p1
    if win=='yes':
       px=os.path.join(os.path.dirname(p1),'lib')
    
    lst=os.listdir(px)
    for fn in lst:
        if win=='yes':
           if fn.startswith('opencv_core'):
              j=fn.find('.')
              if j>0:
                 ver=fn[11:j]
                 break
           elif fn.startswith('opencv_world'):
              j=fn.find('.')
              if j>0:
                 ver=fn[12:j]
                 break

        elif fn.startswith(p0):
           x=fn[len(p0):]
           if x.startswith('.'):
              ver=x[1:]
              break

    return {'return':0, 'cmd':'', 'version':ver}

##############################################################################
# setup environment setup

def setup(i):
    """
    Input:  {
              cfg              - meta of this soft entry
              self_cfg         - meta of module soft
              ck_kernel        - import CK kernel module (to reuse functions)

              host_os_uoa      - host OS UOA
              host_os_uid      - host OS UID
              host_os_dict     - host OS meta

              target_os_uoa    - target OS UOA
              target_os_uid    - target OS UID
              target_os_dict   - target OS meta

              target_device_id - target device ID (if via ADB)

              tags             - list of tags used to search this entry

              env              - updated environment vars from meta
              customize        - updated customize vars from meta

              deps             - resolved dependencies for this soft

              interactive      - if 'yes', can ask questions, otherwise quiet
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0

              bat          - prepared string for bat file
            }

    """

    import os

    # Get variables
    ck=i['ck_kernel']
    s=''

    iv=i.get('interactive','')

    env=i.get('env',{})
    cfg=i.get('cfg',{})
    deps=i.get('deps',{})
    tags=i.get('tags',[])
    cus=i.get('customize',{})

    target_d=i.get('target_os_dict',{})
    win=target_d.get('windows_base','')
    mic=target_d.get('intel_mic','')
    remote=target_d.get('remote','')
    mingw=target_d.get('mingw','')
    tbits=target_d.get('bits','')

    envp=cus.get('env_prefix','')
    pi=cus.get('path_install','')

    hosd=i.get('host_os_dict',{})

    ellp=hosd.get('env_ld_library_path','')
    if ellp=='': ellp='LD_LIBRARY_PATH'
    elp=hosd.get('env_library_path','')
    if elp=='': elp='LIBRARY_PATH'

    fp=cus.get('full_path','')
    pl=os.path.dirname(fp)
    px=os.path.dirname(pl)

    pi=fp
    found=False
    while True:
       if os.path.isdir(os.path.join(pi,'include')):
          found=True
          break
       pix=os.path.dirname(pi)
       if pix==pi:
          break
       pi=pix

    if not found:
       return {'return':1, 'error':'can\'t find root dir of the OpenCL installation'}

    ################################################################
    if remote=='yes':
       cus['path_bin']=pi+'\\OpenCV-android-sdk\\sdk\\native\\bin'
       cus['path_lib']=pi+'\\OpenCV-android-sdk\\sdk\\native\\libs\\armeabi'

       cus['path_include']=pi+'\\opencv-2.4.11\\include'
       cus['path_includes']=[pi+'\\opencv-2.4.11\\3rdparty\\include\\opencl\\1.2']

       cus['path_static_lib']=cus['path_lib']

       cus['static_lib']='libopencv_core.a'

       cus['extra_static_libs']={'opencv_imgproc':'libopencv_imgproc.a',
                                 'opencv_ocl':'libopencv_ocl.a',
                                 'opencv_highgui':'libopencv_highgui.a'}

       env['CK_ENV_LIB_OPENCV_STATIC_LIB_PATH']=cus['path_static_lib']

       if win=='yes':
          s+='\nset '+ellp+'=%CK_ENV_LIB_OPENCV_LIB%;%'+ellp+'%\n'
       else:
          s+='\nexport '+ellp+'=$CK_ENV_LIB_OPENCV_LIB:$'+ellp+'\n'

    elif win=='yes':
       ext='x64'
       if tbits=='32': ext='ia32'

       # Check libs version extensions
       cus['path_bin']=px+'\\bin'
       cus['path_lib']=px+'\\lib'

       cus['path_include']=pi+'/include'

       # Check version
       lst=os.listdir(cus['path_lib'])
       le=''
       for fn in lst:
           if fn.startswith('opencv_core'):
              j=fn.find('.')
              if j>0:
                 le=fn[11:j]
                 break

       cus['path_include']=pi+'/include'

       cus['path_static_lib']=cus['path_lib']
       cus['path_dynamic_lib']=cus['path_bin']

       cus['static_lib']='opencv_core'+le+'.lib'
       cus['dynamic_lib']='opencv_core'+le+'.dll'

       cus['extra_static_libs']={'opencv_imgproc':'opencv_imgproc'+le+'.lib',
                                 'opencv_ocl':'opencv_ocl'+le+'.lib',
                                 'opencv_highgui':'opencv_highgui'+le+'.lib'}
 
       cus['extra_dynamic_libs']={'opencv_imgproc':'opencv_imgproc'+le+'.dll',
                                  'opencv_ocl':'opencv_ocl'+le+'.dll',
                                  'opencv_highgui':'opencv_highgui'+le+'.dll'}

       env['CK_ENV_LIB_OPENCV_STATIC_LIB_PATH']=cus['path_static_lib']
       env['CK_ENV_LIB_OPENCV_DYNAMIC_LIB_PATH']=cus['path_dynamic_lib']

       s+='\nset PATH='+cus['path_bin']+';%PATH%\n'

    else:
       cus['path_lib']=pl

       cus['path_include']=pi+'/include'

       cus['path_static_lib']=cus['path_lib']
       cus['path_dynamic_lib']=cus['path_lib']

       cus['dynamic_lib']='libopencv_core.so'

       cus['extra_dynamic_libs']={'opencv_imgproc':'libopencv_imgproc.so',
                                  'opencv_ocl':'libopencv_ocl.so',
                                  'opencv_highgui':'libopencv_highgui.so'}

       env['CK_ENV_LIB_OPENCV_STATIC_LIB_PATH']=cus['path_static_lib']
       env['CK_ENV_LIB_OPENCV_DYNAMIC_LIB_PATH']=cus['path_dynamic_lib']

       s+='\nexport '+ellp+'=$CK_ENV_LIB_OPENCV_LIB:$'+ellp+'\n'

    return {'return':0, 'bat':s}
