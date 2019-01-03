#!/usr/bin/python3

from optparse import OptionParser
from mako.template import Template
import json
import tempfile
import mcpat
import collections

def update(d, u):
    for k, v in u.items():
        if isinstance(v, collections.Mapping):
            d[k] = update(d.get(k, {}), v)
        else:
            d[k] = v
    return d

def get_system_param(cfg):
    param = {}
    param['number_of_cores'] = len(cfg['system']['timingCpu'])
    param['target_core_clockrate'] = int(1000 / cfg['system']['clk_domain']['clock'][0]) * 1000

    # core0
    param['core0'] = {}
    param['core0']['clock_rate'] = int(1000 / cfg['system']['clk_domain']['clock'][0]) * 1000
    param['core0']['vdd'] = cfg['system']['clk_domain']['voltage_domain']['voltage'][0]
    param['core0']['number_of_BTB'] = 1
    param['core0']['number_of_BPT'] = 1
    param['core0']['fetch_width'] =  cfg['system']['timingCpu'][0]['fetchWidth']
    param['core0']['decode_width'] = cfg['system']['timingCpu'][0]['decodeWidth']
    param['core0']['issue_width'] = cfg['system']['timingCpu'][0]['issueWidth']
    param['core0']['peak_issue_width'] = param['core0']['issue_width']
    param['core0']['commit_width'] = cfg['system']['timingCpu'][0]['commitWidth']
    param['core0']['fp_issue_width'] = int(cfg['system']['timingCpu'][0]['issueWidth'] / 4)
    param['core0']['prediction_width'] = 1
    param['core0']['pipelines_per_core'] = '1, 1'
    param['core0']['pipeline_depth'] = '22, 28'
    param['core0']['ALU_per_core'] = cfg['system']['timingCpu'][0]['fuPool']['FUList'][0]['count']
    param['core0']['MUL_per_core'] = cfg['system']['timingCpu'][0]['fuPool']['FUList'][1]['count']
    param['core0']['FPU_per_core'] = cfg['system']['timingCpu'][0]['fuPool']['FUList'][2]['count']
    param['core0']['instruction_buffer_size'] = cfg['system']['timingCpu'][0]['fetchBufferSize']
    param['core0']['decoded_stream_buffer_size'] = cfg['system']['timingCpu'][0]['numIQEntries']
    param['core0']['instruction_window_scheme'] = 0 # PRF base
    param['core0']['instruction_window_size'] = cfg['system']['timingCpu'][0]['numIQEntries']
    param['core0']['fp_instruction_window_size'] = cfg['system']['timingCpu'][0]['numIQEntries']
    param['core0']['ROB_size'] = cfg['system']['timingCpu'][0]['numROBEntries']
    param['core0']['phy_Regs_IRF_size'] = cfg['system']['timingCpu'][0]['numPhysIntRegs']
    param['core0']['phy_Regs_FRF_size'] = cfg['system']['timingCpu'][0]['numPhysFloatRegs']
    param['core0']['rename_scheme'] = 1 # CAM based
    param['core0']['checkpoint_depth'] = 0
    param['core0']['register_windows_size'] = 0
    param['core0']['LSU_order'] = 'inorder'
    param['core0']['store_buffer_size'] = cfg['system']['timingCpu'][0]['SQEntries']
    param['core0']['load_buffer_size'] = cfg['system']['timingCpu'][0]['LQEntries']
    param['core0']['memory_ports'] = int(cfg['system']['timingCpu'][0]['fuPool']["FUList"][7]['count'] / 2)
    param['core0']['RAS_size'] = int(cfg['system']['timingCpu'][0]['branchPred']['RASSize'])

    param['core0']['PBT'] = {}
    param['core0']['PBT']['local_predictor_size'] = cfg['system']['timingCpu'][0]['branchPred']['localPredictorSize']
    param['core0']['PBT']['local_predictor_entries'] = int(cfg['system']['timingCpu'][0]['branchPred']['localPredictorSize']) / 2
    param['core0']['PBT']['global_predictor_entries'] = int(cfg['system']['timingCpu'][0]['branchPred']['globalPredictorSize']) / 2
    param['core0']['PBT']['global_predictor_bits'] = 2
    param['core0']['PBT']['chooser_predictor_entries'] = int(cfg['system']['timingCpu'][0]['branchPred']['choicePredictorSize']) / 2
    param['core0']['PBT']['chooser_predictor_bits'] = 2

    param['core0']['itlb'] = {}
    param['core0']['itlb']['number_entries'] = cfg['system']['timingCpu'][0]['itb']['size']
    param['core0']['icache'] = {}
    param['core0']['icache']['icache_config'] = "16384,32,8,1,8,3,32,0"
    param['core0']['icache']['buffer_sizes'] = "16, 16, 16, 0"

    param['core0']['dtlb'] = {}
    param['core0']['dtlb']['number_entries'] = cfg['system']['timingCpu'][0]['dtb']['size']
    param['core0']['dcache'] = {}
    param['core0']['dcache']['dcache_config'] = "16384, 16, 4, 1, 3, 3, 16, 1"
    param['core0']['dcache']['buffer_sizes'] = "16, 16, 16, 16"

    param['core0']['BTB'] = {}
    param['core0']['BTB']['BTB_config'] = "5120, 4, 2, 1, 1, 3"

    param['L1Directory0'] = {}
    param['L1Directory0']['Directory_type'] = 0
    param['L1Directory0']['Dir_config'] = "4096, 2, 0, 1, 100, 100, 8"
    param['L1Directory0']['buffer_sizes'] = "8, 8, 8, 8"
    param['L1Directory0']['clockrate'] = 3000
    param['L1Directory0']['vdd'] = 0
    param['L1Directory0']['power_gating_vcc'] = -1
    param['L1Directory0']['ports'] = '1, 1, 1'
    param['L1Directory0']['device_type'] = 0

    param['L2Directory0'] = {}
    param['L2Directory0']['Directory_type'] = 0
    param['L2Directory0']['Dir_config'] = "1048576, 16, 16, 1, 2, 100"
    param['L2Directory0']['buffer_sizes'] = "8, 8, 8, 8"
    param['L2Directory0']['clockrate'] = 3000
    param['L2Directory0']['vdd'] = 0
    param['L2Directory0']['power_gating_vcc'] = -1
    param['L2Directory0']['ports'] = '1, 1, 1'
    param['L2Directory0']['device_type'] = 0

    param['L20'] = {}
    param['L20']['L2_config'] = "1048576,32, 8, 8, 8, 23, 32, 1"
    param['L20']['buffer_sizes'] = "16, 16, 16, 16"
    param['L20']['clockrate'] = 3000
    param['L20']['vdd'] = 0
    param['L20']['ports'] = '1, 1, 1'
    param['L20']['device_type'] = 0

    param['L30'] = {}
    param['L30']['L3_config'] = '16777216, 64, 16, 16, 16, 100, 1'
    param['L30']['clockrate'] = 3000
    param['L30']['ports'] = '1, 1, 1'
    param['L30']['device_type'] = 0
    param['L30']['vdd'] = 0
    param['L30']['power_gating_vcc'] = -1
    param['L30']['buffer_sizes'] = '16, 16, 16, 16'


    param['noc0'] = {}
    param['noc0']['clockrate'] = 3000
    param['noc0']['link_throughput'] = 1
    param['noc0']['link_latency'] = 1

    param['mc'] = {}
    param['mc']['mc_clock'] = 2400
    param['mc']['vdd'] = 0
    param['mc']['peak_transfer_rate'] = 4800
    param['mc']['block_size'] = 64
    param['mc']['number_mcs'] = 0
    param['mc']['memory_channels_per_mc'] = 1
    param['mc']['number_ranks'] = 2
    param['mc']['req_window_size_per_channel'] = 32
    param['mc']['IO_buffer_size_per_channel'] = 32
    param['mc']['databus_width'] = 128
    param['mc']['addressbus_width'] = 51

    return param

def read_stats(fp):
    stsString = ''
    started = False
    line = fp.readline()
    while(line):
        if started:
            if -1 != line.find('End Simulation Statistics'):
                return stsString
            stsString = stsString + line
            line = fp.readline()
        else:
            if -1 == line.find('Begin Simulation Statistics'):
                pass
            else:
                started = True
            line = fp.readline()

def get_system_stats(stsString, commitWidth = 4):
    stats = {}
    stsDict = {}
    stsLines = stsString.splitlines()
    for l in stsLines:
        stsList = l.split()
        if stsList:
            stsDict.update({stsList[0]: stsList[1]})

    # Processor
    stats['total_cycles'] = stsDict.get('system.timingCpu.numCycles', 0)
    stats['idle_cycles'] = stsDict.get('system.timingCpu.idleCycles', 0)
    stats['busy_cycles'] = int(stats['total_cycles']) - int(stats['idle_cycles'])

    # Core0
    stats['core0'] = {}
    stats['core0']['total_instructions'] = stsDict.get('system.timingCpu.commit.committedOps', 0)
    stats['core0']['int_instructions'] = stsDict.get('system.timingCpu.commit.int_insts', 0)
    stats['core0']['fp_instructions'] = stsDict.get('system.timingCpu.commit.fp_insts', 0)
    stats['core0']['branch_instructions'] = stsDict.get('system.timingCpu.commit.branches', 0)
    stats['core0']['branch_mispredictions'] = stsDict.get('system.timingCpu.commit.branchMispredicts', 0)
    stats['core0']['load_instructions'] = stsDict.get('system.timingCpu.commit.loads', 0)
    stats['core0']['store_instructions'] = stsDict.get('system.timingCpu.iew.exec_stores', 0)
    stats['core0']['committed_instructions'] = stsDict.get('system.timingCpu.commit.committedOps', 0)
    stats['core0']['committed_int_instructions'] = stsDict.get('system.timingCpu.commit.int_insts', 0)
    stats['core0']['committed_fp_instructions'] = stsDict.get('system.timingCpu.commit.fp_insts', 0)
    stats['core0']['pipeline_duty_cycle'] = float(stsDict.get('system.timingCpu.ipc', 0)) / commitWidth
    stats['core0']['total_cycles'] = stsDict.get('system.timingCpu.numCycles', 0)
    stats['core0']['idle_cycles'] = stsDict.get('system.timingCpu.idleCycles', 0)
    stats['core0']['busy_cycles'] = int(stats['core0']['total_cycles']) - int(stats['core0']['idle_cycles'])
    stats['core0']['ROB_reads'] = stsDict.get('system.timingCpu.rob.rob_reads', 0)
    stats['core0']['ROB_writes'] = stsDict.get('system.timingCpu.rob.rob_writes', 0)
    stats['core0']['rename_reads'] = stsDict.get('system.timingCpu.rename.RenameLookups', 0)
    stats['core0']['rename_writes'] = stsDict.get('system.timingCpu.rename.RenamedOperands', 0)
    stats['core0']['fp_rename_reads'] = stsDict.get('system.timingCpu.rename.fp_rename_lookups', 0)
    stats['core0']['fp_rename_writes'] = 0.3 * float(stsDict.get('system.timingCpu.rename.RenamedOperands', 0)) # FIXME
    stats['core0']['inst_window_reads'] = stsDict.get('system.timingCpu.iq.int_inst_queue_reads', 0)
    stats['core0']['inst_window_writes'] = stsDict.get('system.timingCpu.iq.int_inst_queue_writes', 0)
    stats['core0']['inst_window_wakeup_accesses'] = stsDict.get('system.timingCpu.iq.int_inst_queue_wakeup_accesses', 0)
    stats['core0']['fp_inst_window_reads'] = stsDict.get('system.timingCpu.iq.fp_inst_queue_reads', 0)
    stats['core0']['fp_inst_window_writes'] = stsDict.get('system.timingCpu.iq.vec_inst_queue_writes', 0)
    stats['core0']['fp_inst_window_wakeup_accesses'] = stsDict.get('system.timingCpu.iq.fp_inst_queue_wakeup_accesses', 0)
    stats['core0']['int_regfile_reads'] = stsDict.get('system.timingCpu.int_regfile_reads', 0)
    stats['core0']['int_regfile_writes'] = stsDict.get('system.timingCpu.int_regfile_writes', 0)
    stats['core0']['float_regfile_reads'] = stsDict.get('system.timingCpu.fp_regfile_reads', 0)
    stats['core0']['float_regfile_writes'] = stsDict.get('system.timingCpu.fp_regfile_writes', 0)
    stats['core0']['function_calls'] = stsDict.get('system.timingCpu.commit.function_calls', 0)
    stats['core0']['context_switches'] = 0
    stats['core0']['ialu_accesses'] = stsDict.get('system.timingCpu.iq.int_alu_accesses', 0)
    stats['core0']['fpu_accesses'] = stsDict.get('system.timingCpu.iq.fp_alu_accesses', 0)
    stats['core0']['mul_accesses'] = 0
    stats['core0']['cdb_alu_accesses'] = 0
    stats['core0']['cdb_mul_accesses'] = 0
    stats['core0']['cdb_fpu_accesses'] = 0
    stats['core0']['itlb'] = {}
    stats['core0']['itlb']['total_accesses'] = stsDict.get('system.timingCpu.itb.wrAccesses', 0)
    stats['core0']['itlb']['total_misses'] = stsDict.get('system.timingCpu.itb.wrMisses', 0)
    stats['core0']['itlb']['conflicts'] = 0
    stats['core0']['icache'] = {}
    stats['core0']['icache']['read_accesses'] = stsDict.get('system.cpu.icache.ReadReq_accesses::total', 0)
    stats['core0']['icache']['read_misses'] = stsDict.get('system.cpu.icache.ReadReq_misses::total', 0)
    stats['core0']['icache']['conflicts'] = 0
    stats['core0']['dtlb'] = {}
    stats['core0']['dtlb']['total_accesses'] = \
            int(stsDict.get('system.timingCpu.dtb.rdAccesses', 0)) + int(stsDict.get('system.timingCpu.dtb.wrAccesses', 0))
    stats['core0']['dtlb']['total_misses'] = \
            int(stsDict.get('system.timingCpu.dtb.rdMisses', 0)) + int(stsDict.get('system.timingCpu.dtb.wrMisses', 0))
    stats['core0']['dtlb']['conflicts'] = 0
    stats['core0']['dcache'] = {}
    stats['core0']['dcache']['read_accesses'] = stsDict.get('system.cpu.dcache.ReadReq_accesses::total', 0)
    stats['core0']['dcache']['write_accesses'] = stsDict.get('system.cpu.dcache.WriteReq_accesses::total', 0)
    stats['core0']['dcache']['read_misses'] = stsDict.get('system.cpu.dcache.ReadReq_misses::total', 0)
    stats['core0']['dcache']['write_misses'] = stsDict.get('system.cpu.dcache.WriteReq_misses::total', 0)
    stats['core0']['dcache']['conflicts'] = 0
    stats['core0']['BTB'] = {}
    stats['core0']['BTB']['read_accesses'] = stsDict.get('system.timingCpu.branchPred.BTBLookups', 0)
    stats['core0']['BTB']['write_accesses'] = \
            int(stsDict.get('system.timingCpu.branchPred.BTBLookups', 0)) - int(stsDict.get('system.timingCpu.branchPred.BTBHits', 0))

    stats['L1Directory0'] = {}
    stats['L1Directory0']['read_accesses'] = 0
    stats['L1Directory0']['write_accesses'] = 0
    stats['L1Directory0']['read_misses'] = 0
    stats['L1Directory0']['write_misses'] = 0
    stats['L1Directory0']['conflicts'] = 0

    stats['L2Directory0'] = {}
    stats['L2Directory0']['read_accesses'] = 0
    stats['L2Directory0']['write_accesses'] = 0
    stats['L2Directory0']['read_misses'] = 0
    stats['L2Directory0']['write_misses'] = 0
    stats['L2Directory0']['conflicts'] = 0

    stats['L20'] = {}
    stats['L20']['read_accesses']= 0
    stats['L20']['write_accesses'] = 0
    stats['L20']['read_misses'] = 0
    stats['L20']['write_misses'] = 0
    stats['L20']['conflicts'] = 0

    stats['L30'] = {}
    stats['L30']['read_accesses'] = 0
    stats['L30']['write_accesses'] = 0
    stats['L30']['read_misses'] = 0
    stats['L30']['write_misses'] = 0
    stats['L30']['conflicts'] = 0

    stats['noc0'] = {}
    stats['noc0']['total_accesses'] = 0

    stats['mc'] = {}
    stats['mc']['memory_accesses'] = 0
    stats['mc']['memory_reads'] = 0
    stats['mc']['memory_writes'] = 0

    return stats

if __name__ == "__main__":
    parser = OptionParser()

    parser.add_option("-c", "--config", dest="config",
                    help="gem5 full system configure file in json format" )
    parser.add_option("-s", "--stats", dest="stats",
                    help="gem5 status file in txt format")
    parser.add_option("-t", "--template", dest="template",
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

    system = update(system, get_system_param(cfg))

    # Get system status slice by slice
    fp = open(opts.stats, 'r')

    mkt = Template(filename = opts.template)
    while(1):
        sts = read_stats(fp)
        if sts:
            system = update(system, get_system_stats(sts))

            # Create a tempfile
            tp = tempfile.NamedTemporaryFile(mode='wt')

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
