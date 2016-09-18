#
# Collective Knowledge (description of a given device for crowd-benchmarking and crowd-tuning)
#
# See CK LICENSE.txt for licensing details
# See CK COPYRIGHT.txt for copyright details
#
# Developer: Grigori Fursin, Grigori.Fursin@cTuning.org, http://fursin.net
#

cfg={}  # Will be updated by CK (meta description of this module)
work={} # Will be updated by CK (temporal data)
ck=None # Will be updated by CK (initialized CK kernel) 

# Local settings
line='***************************************************************************************'

##############################################################################
# Initialize module

def init(i):
    """

    Input:  {}

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """
    return {'return':0}

##############################################################################
# add new device description

def add(i):
    """
    Input:  {
              (data_uoa) or (alias)        - force name of CK entry to store description of this device
                                             (if empty, suggest automatically)

              (host_os)                    - host OS (detect, if omitted)
              (target_os)                  - OS module to check (if omitted, analyze host)
              (device_id)                  - device id if remote (such as adb)

              (use_host)                   - if 'yes', configure host as target

              (access_type)                - access type to the device ("android", "mingw", "wa", "ck_node", "ssh")

              (share)                      - if 'yes', share public info about platform with the community via cknowledge.org/repo
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    # Setting output
    o=i.get('out','')
    oo=''
    if o=='con': oo='con'

    # Params
    hos=i.get('host_os','')
    tos=i.get('target_os', '')
    tdid=i.get('device_id', '')

    host=i.get('use_host','')
    at=i.get('access_type','')

    duoa=i.get('data_uoa','')
    if duoa=='':
       duoa=i.get('alias','')

    exc='no'
    if i.get('share',''):
        exc='yes'

    er=i.get('exchange_repo','')
    esr=i.get('exchange_subrepo','')

    dp='' # detect platform

    # Check host target
    if tos=='' and host=='':
        if o=='con':
            ck.out(line)

            r=ck.inp({'text':'Would you like use your host as a target device for experiments (y/N): '})
            x=r['string'].strip().lower()
    
            if x=='y' or x=='yes':
                host='yes'
        else:
            host='yes'

    # If not host target
    if host!='yes' and tos=='' and at=='':
        if o=='con':
            tat=cfg['target_access_types']

            ck.out(line)

            r=ck.select({'title':'Select access type to your target device: ',
                         'dict':tat})
            if r['return']>0: return r
            at=r['string']

            tags=tat[at]['tags']
            dp=tat[at]['detect_platform']
            dos=''

            # Extra checks
            if tags=='android-with-arch':
                # Check preliminary Android parameters including arch + API to finalize detecton of the CK OS description
                if o=='con':
                    ck.out(line)
                    ck.out('Attempting to detect Android API and arch ...')
                    ck.out('')
                 
                ii={'action':'detect',
                    'host_os':hos,
                    'target_os':'android-32',
                    'module_uoa':cfg['module_deps']['platform.cpu'],
                    'out':oo}
                r=ck.access(ii)
                if r['return']>0: return r

                tdid=r['device_id']

                params=r['features']['os_misc'].get('adb_params',{})

                sdk=str(params.get('ro.build.version.sdk',''))
                abi=str(params.get('ro.product.cpu.abi',''))

                if sdk!='':
                    if o=='con':
                       ck.out('')
                       ck.out('Android API: '+sdk)

                    tags+=',android-'+sdk
 
                if abi!='':
                    if o=='con':
                       ck.out('')
                       ck.out('Android ABI: '+abi)

                    if abi.startswith('arm64'):
                        dos='*-arm64'
                    elif abi.startswith('arm'):
                        dos='*-arm'

            # Search OS
            ii={'action':'search',
                'module_uoa':cfg['module_deps']['os'],
                'data_uoa':dos,
                'tags':tags}
            r=ck.access(ii)
            if r['return']>0: return r

            lst=r['lst']

            if len(lst)==0:
                return {'return':1, 'error':'no OS found for tags "'+tags+'" and OS wildcard "'+dos+'"'}
            elif len(lst)==1:
                tos=lst[0]['data_uoa']
            else:
                ck.out(line)
                ck.out('Select most close OS and architecture on a target device:')
                ck.out('')

                r=ck.select_uoa({'choices':lst})
                if r['return']>0: return r
                tos=r['choice']

    # Target OS should be finalized
    if host!='yes' and tos=='':
        return {'return':1, 'error':'no target os selected'}

    # Get user friend alias of OS
    if tos!='':
       r=ck.access({'action':'load',
                    'module_uoa':cfg['module_deps']['os'],
                    'data_uoa':tos})
       if r['return']>0: return r
       tos=r['data_uoa']

    if o=='con':
        if tos!='':
            ck.out(line)
            ck.out('Selected target OS UOA:    '+tos)

        if tdid!='':
            ck.out('Selected target device ID: '+tdid)

    # Detect various parameters of the platform (to suggest platform name as well)
    pn=''
    if dp=='yes' or host=='yes':
        if o=='con':
            ck.out(line)
            ck.out('Attempting to detect various parameters of your target device ...')
            ck.out('')
         
        ii={'action':'detect',
            'host_os':hos,
            'target_os':tos,
            'device_id':tdid,
            'module_uoa':cfg['module_deps']['platform'],
            'use_host':host,
            'exchange':exc,
            'exchange_repo':er,
            'exchange_subrepo':esr,
            'out':oo}
        rp=ck.access(ii)
        if rp['return']>0: return rp

        pn=rp.get('features',{}).get('platform',{}).get('name','')

    # Suggest platform name
    if duoa=='':
        if pn!='' and o=='con':
            ck.out(line)
            ck.out('Detected target device name: '+pn)
            ck.out('')

        if host=='yes':
            duoa='host'
        elif pn!='':
            duoa=pn.lower().replace(' ','-').replace('_','-')

        if o=='con':
            s='Enter alias for your device to be recorded in your CK local repo'
        
            if duoa!='':
                s+=' or press Enter for "'+duoa+'"'

            s+=' : '

            ck.out('')

            r=ck.inp({'text':s})
            x=r['string'].strip()

            if x!='': duoa=x

    # Check that alias is there
    if duoa=='':
        return {'return':1, 'error':'device alias is not defined'}

    # Check if entry already exists
    ii={'action':'load',
        'module_uoa':work['self_module_uid'],
        'data_uoa':duoa}
    r=ck.access(ii)
    if r['return']>0 and r['return']!=16:
        return r

    if r['return']==0:
        renew=False

        s='CK entry "device:'+duoa+'" already exists'
        if o=='con':
            ck.out('')

            r=ck.inp({'text':s+'. Renew (Y/n)? '})
            x=r['string'].strip().lower()

            if x=='' or x=='y' or x=='yes':
                renew=True
            else:
                return {'return':0}
 
        if not renew:
            return {'return':1, 'error':s}

    # Add device entry
    dd={'host_os':hos,
        'target_os':tos,
        'target_device_id':tdid,
        'host_os_uoa':rp.get('host_os_uoa',''),
        'host_os_uid':rp.get('host_os_uid',''),
        'host_os_dict':rp.get('host_os_dict',{}),
        'target_os_uoa':rp.get('os_uoa',''),
        'target_os_uid':rp.get('os_uid',''),
        'target_os_dict':rp.get('os_dict',{}),
        'access_type':at,
        'use_host':host,
        'features':rp['features']}

    ii={'action':'update',
        'module_uoa':work['self_module_uid'],
        'data_uoa':duoa,
        'dict':dd,
        'substitute':'yes',
        'sort_keys':'yes'}
    r=ck.access(ii)
    if r['return']>0: return r

    duoa=r['data_uoa']
    duid=r['data_uid']

    # Success
    if o=='con':
        ck.out(line)
        ck.out('Your target device was successfully registered in CK with alias: '+duoa+' ('+duid+')')

    return {'return':0}

##############################################################################
# show available target devices and their status

def show(i):
    """
    Input:  {
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    o=i.get('out','')

    if o=='con':
       ck.out(line)
       ck.out('Checking devices ...')
       ck.out('')

    c=''
    h='<center>\n'

    c='Available target devices and their status:'

    h+='<h2>'+c+'</h2>\n'

    # Check host URL prefix and default module/action
    rx=ck.access({'action':'form_url_prefix',
                  'module_uoa':'wfe',
                  'host':i.get('host',''), 
                  'port':i.get('port',''), 
                  'template':i.get('template','')})
    if rx['return']>0: return rx
    url0=rx['url']
    template=rx['template']

    url=url0
    action=i.get('action','')
    muoa=i.get('module_uoa','')

    st=''

    url+='action=index&module_uoa=wfe&native_action='+action+'&'+'native_module_uoa='+muoa
    url1=url

    # List entries
    r=ck.access({'action':'search',
                 'module_uoa':work['self_module_uid'],
                 'add_meta':'yes'})
    if r['return']>0: return r

    lst=r['lst']

    h+='<table border="1" cellpadding="7" cellspacing="0">\n'

    h+='  <tr>\n'
    h+='   <td align="center"><b>CK alias</b></td>\n'
    h+='   <td align="center"><b>Real device name</b></td>\n'
    h+='   <td align="center"><b>ID</b></td>\n'
    h+='   <td align="center"><b>CK OS</b></td>\n'
    h+='   <td align="center"><b>Real OS name</b></td>\n'
    h+='   <td align="center"><b>CPUs</b></td>\n'
    h+='   <td align="center"><b>GPU</b></td>\n'
    h+='   <td align="center"><b>GPGPU</b></td>\n'
    h+='   <td align="center"><b>Status</b></td>\n'
    h+='  <tr>\n'

    c+='\n'
    for q in sorted(lst, key = lambda v: v['data_uoa']):
        duoa=q['data_uoa']
        duid=q['data_uid']
        d=q['meta']

        hos=d.get('host_os_uoa','')

        tos=d.get('target_os_uoa','')
        tos_uid=d.get('target_os_uid','')

        tdid=d.get('target_device_id','')

        # Check if device connected
        connected=False

        uh=d.get('use_host','')
        if uh=='yes':
            connected=True
        else:
            # Check status of remote
            connected=False

            at=d.get('access_type','')
            if at=='android' or at=='wa_android':
                # Attempt to get Android features 
                ii={'action':'detect',
                    'module_uoa':cfg['module_deps']['platform.os'],
                    'host_os':hos,
                    'target_os':tos,
                    'device_id':tdid}
                r=ck.access(ii)

#                import json
#                h+='<hr><pre>'+json.dumps(r,indent=2)+'</pre>'

                if r['return']==0:
                   connected=True

        # Prepare info
        if connected:
            ss=' style="background-color:#009f00;color:#ffffff"'
            sx='Connected'
        else:
            ss=' style="background-color:#9f0000;color:#ffffff;"'
            sx='???'

        h+='  <tr>\n'

        ft=d.get('features',{})
        rn=ft.get('platform',{}).get('name','')

        on=ft.get('os',{}).get('name','')

        cpus=''
        for q in ft.get('cpu_unique',[]):
            x=q.get('ck_cpu_name','')
            if x!='':
                if cpus!='': 
                    cpus+='<br>\n'
                cpus+=x

        gpu=ft.get('gpu',{}).get('name','')

        gpgpus=''

        # Prepare HTML
        c+='\n'
        c+=duoa+': '
        h+='   <td align="left"><a href="'+url0+'&wcid='+work['self_module_uid']+':'+duid+'">'+duoa+'</a></td>\n'

        h+='   <td align="center">'+rn+'</td>\n'

        h+='   <td align="center">'+tdid+'</td>\n'

        h+='   <td align="left"><a href="'+url0+'&wcid='+cfg['module_deps']['os']+':'+tos_uid+'">'+tos+'</a></td>\n'

        h+='   <td align="center">'+on+'</td>\n'

        h+='   <td align="center">'+cpus+'</td>\n'

        h+='   <td align="center">'+gpu+'</td>\n'

        h+='   <td align="center">'+gpgpus+'</td>\n'

        c+=sx
        h+='   <td align="center"'+ss+'>'+sx+'</td>\n'

        h+='  <tr>\n'

    h+='</table>\n'
    h+='</center>\n'

    if o=='con':
       ck.out(line)
       ck.out(c)

    return {'return':0, 'html':h, 'style':st}

##############################################################################
# view devices in the browser

def browse(i):
    """
    Input:  {
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    i['action']='start'
    i['cid']=''
    i['module_uoa']='web'
    i['browser']='yes'
    i['extra_url']='action=index&module_uoa=wfe&native_action=show&native_module_uoa=device'
    i['template']=''

    return ck.access(i)
