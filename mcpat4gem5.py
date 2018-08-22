#!/usr/bin/python2

from optparse import OptionParser
import json
import mako
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
    

    
    return param

def get_system_stats():
    pass
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
    with open(opts.config, 'r') as fp:
        cfg = json.load(fp)
   
    system.update(get_system_param(cfg))
    cfg.close()

    
    p1 = mcpat.ParseXML()
    p1.parse(opts.infile)

    proc = mcpat.Processor(p1)
    proc.displayEnergy(2, opts.plevel)

    exit(0)
