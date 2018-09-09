#!/usr/bin/python2

from optparse import OptionParser
import json
import mako
import tempfile
import mcpat

def get_system_param(cfg):
    param = {}
    param['number_of_cores'] = len(cfg['system']['timingCPU'])
    param['target_core_clockrate'] = int(1000 / cfg['system']['clk_domain']['clock'][0])

    # core0
    param['core0']['clock_rate'] = int(1000 / cfg['system']['clk_domain']['clock'][0])
    param['core0']['vdd'] = cfg['system']['clk_domain']['voltage_domain']['voltage'][0]
    param['core0']['number_of_BTB'] = 1
    param['core0']['number_of_BPT'] = 1
    param['core0']['fetch_width'] =  cfg['system']['timingCPU'][0]['fetchWidth']
    param['core0']['decode_width'] = cfg['system']['timingCPU'][0]['decodeWidth']
    param['core0']['issue_width'] = cfg['system']['timingCPU'][0]['issueWidth']
    param['core0']['peak_issue_width'] = param['core0']['issue_width']
    param['core0']['commit_width'] = cfg['system']['timingCPU'][0]['commitWidth']
    param['core0']['fp_issue_width'] = int(cfg['system']['timingCPU'][0]['issueWidth'] / 4)
    param['core0']['prediction_width'] = 1
    param['core0']['pipelines_per_core'] = '1, 1'
    param['core0']['pipeline_depth'] = '22, 28'
    param['core0']['ALU_per_core'] = cfg['system']['timingCPU'][0]['fuPool']['FUList'][0]['count']
    param['core0']['MUL_per_core'] = cfg['system']['timingCPU'][0]['fuPool']['FUList'][1]['count']
    param['core0']['FPU_per_core'] = cfg['system']['timingCPU'][0]['fuPool']['FUList'][2]['count']
    param['core0']['instruction_buffer_size'] = cfg['system']['timingCPU'][0]['fetchBufferSize']
    param['core0']['decoded_stream_buffer_size'] = cfg['system']['timingCPU'][0]['numIQEntries']
    param['core0']['instruction_window_scheme'] = 0 # PRF base
    param['core0']['instruction_window_size'] = cfg['system']['timingCPU'][0]['numIQEntries']
    param['core0']['fp_instruction_window_size'] = cfg['system']['timingCPU'][0]['numIQEntries']
    param['core0']['ROB_size'] = cfg['system']['timingCPU'][0]['numROBEntries']
    param['core0']['phy_Regs_IRF_size'] = cfg['system']['timingCPU'][0]['numPhysIntRegs']
    param['core0']['phy_Regs_FRF_size'] = cfg['system']['timingCPU'][0]['numPhysFloatRegs']
    param['core0']['rename_scheme'] = 1 # CAM based
    param['core0']['checkpoint_depth'] = 0
    param['core0']['register_windows_size'] = 0
    param['core0']['LSU_order'] = 'inorder'
    param['core0']['store_buffer_size'] = cfg['system']['timingCPU'][0]['SQEntries']
    param['core0']['load_buffer_size'] = cfg['system']['timingCPU'][0]['LQEntries']
    param['core0']['memory_ports'] = int(cfg['system']['timingCPU'][0]['FUPool'][7]['count'] / 2)
    param['core0']['RAS_size'] = int(cfg['system']['timingCPU'][0]['branchPred']['RASSize'])

    return param

def read_stats(fp):
    stsString = ''
    started = False
    line = fp.readline()
    while(1):
        if started:
            if -1 != line.find('End Simulation Statistics'):
                return stsString
            stsString = stsString + line
            line = fp.readline()
        else:
            if -1 == line.find('Begin Simulation Statistics'):
                break
            else:
                started = True

def get_system_stats(stsString, commitWidth = 4):
    system = {}
    stsLines = stsString.splitlines()
    for l in stsLines:
        stsList = l.split()
        for item in stsList:
            stsDict.update({item[0]: item[1]})

        # Core0
        system['core0']['total_instructions'] = stsDict['system.timingCpu.commit.committedOps']
        system['core0']['int_instructions'] = stsDict['system.timingCpu.commit.int_insts']
        system['core0']['fp_instructions'] = stsDict['system.timingCpu.commit.fp_insts']
        system['core0']['branch_instructions'] = stsDict['system.timingCpu.commit.branches']
        system['core0']['branch_mispredictions'] = stsDict['system.timingCpu.commit.branchMispredicts']
        system['core0']['load_instructions'] = stsDict['system.timingCpu.commit.loads']
        system['core0']['store_instructions'] = stsDict['system.timingCpu.iew.exec_stores']
        system['core0']['committed_instructions'] = stsDict['system.timingCpu.commit.committedOps']
        system['core0']['committed_int_instructions'] = stsDict['system.timingCpu.commit.int_insts']
        system['core0']['committed_fp_instructions'] = stsict['system.timingCpu.commit.fp_insts']
        system['core0']['pipeline_duty_cycle'] = stsDict['system.timingCpu.ipc'] / commitWidth
        system['core0']['total_cycles'] = stsDict['system.timingCpu.numCycles']
        system['core0']['idle_cycles'] = stsDict['system.timingCpu.idleCycles']
        system['core0']['busy_cycles'] = system['core0']['total_cycles'] - system['core0']['idle_cycles']




if __name__ == "__main__":
    parser = OptionParser()

    parser.add_option("-c", "--config", dest="config",
                    help="gem5 full system configure file in json format" )
    parser.add_option("-s", "--stats", dest="stats",
                    help="gem5 status file in txt format")
    parser.add_option("-t", "--template", dest="template`",
                    help="Template xml file for McPAT")
    parser.add_option("--print_level", dest="plevel", default=0,
                    help="level of details 0~5")
    parser.add_option("--opt_for_clk", dest="opt_for_clk", default=1,
                    help="0:optimize for ED^2P only, 1:optimzed for target clock rate")

    (opts, args) = parser.parse_args()
    mcpat.cvar.opt_for_clk = bool(opts.opt_for_clk)

    system = {}
    # Get system configure
    with open(opts.config, 'r') as fp:
        cfg = json.load(fp)

    system.update(get_system_param(cfg))

    # Get system status slice by slice
    fp = open(opts.stats, 'r')

    mkt = Template(filename = opts.template)
    while(1):
        sts = read_stats(fp)
        if sts:
            system.update(get_system_stats(sts))

            # Create a tempfile
            tp = tempfile.NamedTemporaryFile()

            # Render tmpfile
            print(mkt.render(system = system), file=tp)

            # Create mcpat model
            p1 = mcpat.ParseXML()
            p1.parse(tp.name)

            # Calculate slice's energy
            proc = mcpat.Processor(p1)
            proc.displayEnergy(2, opts.plevel)
        else:
            break

    fp.close()
    exit(0)
