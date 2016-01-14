hp93000,testflow,0.1
language_revision = 1;

testmethodparameters

tm_1:
  "Source_label" = "No";
  "Source_start_vector" = "101";
tm_10:
  "ComplementBurst" = "No";
  "ComplementBurstName" = "";
  "Corner" = "";
  "Dummy_label_name" = "";
  "Func_limit_name" = "";
  "Init_limit_name" = "";
  "Init_pattern" = "";
  "Interleave_init_pattern" = "No";
  "Mask_pins" = "No";
  "Masked_pins" = "";
  "Results_per_label" = "Yes";
  "Retest" = "No";
  "Site_match_mode" = "No";
  "SpeedSort" = "No";
  "SpeedSortAdaptiveSpec" = "No";
  "Stop_on_fail" = "No";
  "Util_purpose_off" = "";
  "Util_purpose_on" = "";
tm_2:
  "Limit_names" = "";
  "diffPosPin" = "pmcsense0";
  "forcePin" = "pmcforce0";
  "jtagTdiPin" = "done";
  "loopCountLimit" = "50";
  "mSettlingTime_ms" = "1";
  "sensePin" = "pmcsense0";
  "subTestName" = "ODP_NullDutTest_st";
  "testPattern" = "ODP_XTR_VIA_PMC_1";
  "vDeltaLimit" = "0.005";
tm_3:
  "ActivateSetVariables" = "0";
  "Limit_names" = "";
  "XtrMode" = "CORE_HVT";
  "diffPosPin" = "pmcsense0";
  "forcePin" = "pmcforce0";
  "jtagTdiPin" = "done";
  "loopCountLimit" = "20";
  "mSettlingTime_ms" = "1";
  "sensePin" = "pmcsense0";
  "subTestName" = "ODP_XtrIdriveTest_st";
  "testPattern" = "ODP_XTR_VIA_PMC_1";
  "vDeltaLimit" = "0.005";
tm_4:
  "ActivateSetVariables" = "0";
  "Limit_names" = "";
  "XtrMode" = "CORE_SVT";
  "diffPosPin" = "pmcsense0";
  "forcePin" = "pmcforce0";
  "jtagTdiPin" = "done";
  "loopCountLimit" = "20";
  "mSettlingTime_ms" = "1";
  "sensePin" = "pmcsense0";
  "subTestName" = "ODP_XtrIdriveTest_st";
  "testPattern" = "ODP_XTR_VIA_PMC_1";
  "vDeltaLimit" = "0.005";
tm_5:
  "ActivateSetVariables" = "0";
  "Limit_names" = "";
  "XtrMode" = "CORE_LVT";
  "diffPosPin" = "pmcsense0";
  "forcePin" = "pmcforce0";
  "jtagTdiPin" = "done";
  "loopCountLimit" = "20";
  "mSettlingTime_ms" = "1";
  "sensePin" = "pmcsense0";
  "subTestName" = "ODP_XtrIdriveTest_st";
  "testPattern" = "ODP_XTR_VIA_PMC_1";
  "vDeltaLimit" = "0.005";
tm_6:
  "ActivateSetVariables" = "0";
  "Limit_names" = "";
  "XtrMode" = "1P5V_DUT";
  "diffPosPin" = "pmcsense0";
  "forcePin" = "pmcforce0";
  "jtagTdiPin" = "done";
  "loopCountLimit" = "20";
  "mSettlingTime_ms" = "1";
  "sensePin" = "pmcsense0";
  "subTestName" = "ODP_XtrIdriveTest_st";
  "testPattern" = "ODP_XTR_VIA_PMC_1";
  "vDeltaLimit" = "0.005";
tm_7:
  "ActivateSetVariables" = "0";
  "Limit_names" = "";
  "XtrMode" = "1P8V_DUT";
  "diffPosPin" = "pmcsense0";
  "forcePin" = "pmcforce0";
  "jtagTdiPin" = "done";
  "loopCountLimit" = "20";
  "mSettlingTime_ms" = "1";
  "sensePin" = "pmcsense0";
  "subTestName" = "ODP_XtrIdriveTest_st";
  "testPattern" = "ODP_XTR_VIA_PMC_1";
  "vDeltaLimit" = "0.005";
tm_8:
  "ActivateSetVariables" = "0";
  "Limit_names" = "";
  "XtrMode" = "SRAM";
  "diffPosPin" = "pmcsense0";
  "forcePin" = "pmcforce0";
  "jtagTdiPin" = "done";
  "loopCountLimit" = "20";
  "mSettlingTime_ms" = "1";
  "sensePin" = "pmcsense0";
  "subTestName" = "ODP_XtrIdriveTest_st";
  "testPattern" = "ODP_XTR_VIA_PMC_1";
  "vDeltaLimit" = "0.005";
tm_9:
  "Limit_names" = "";
  "XtrMode" = "CORE_HVT";
  "diffPosPin" = "pmcsense0";
  "forcePin" = "pmcforce0";
  "index1" = "125";
  "index2" = "125";
  "jtagTdiPin" = "done";
  "mSettlingTime_ms" = "1";
  "sensePin" = "pmcsense0";
  "subTestName" = "ODP_XtrVtTest_st";
  "testPattern" = "ODP_XTR_VIA_PMC_1";

end
-----------------------------------------------------------------
testmethodlimits
end
-----------------------------------------------------------------
testmethods

tm_1:
  testmethod_class = "ti_tml.ODP.RingOscillator";
tm_10:
  testmethod_class = "ti_tml.Digital.Functional";
tm_2:
  testmethod_class = "ti_tml.ODP.NullDutTest";
tm_3:
  testmethod_class = "ti_tml.ODP.XtrIdriveTest_usingCsv";
tm_4:
  testmethod_class = "ti_tml.ODP.XtrIdriveTest_usingCsv";
tm_5:
  testmethod_class = "ti_tml.ODP.XtrIdriveTest_usingCsv";
tm_6:
  testmethod_class = "ti_tml.ODP.XtrIdriveTest_usingCsv";
tm_7:
  testmethod_class = "ti_tml.ODP.XtrIdriveTest_usingCsv";
tm_8:
  testmethod_class = "ti_tml.ODP.XtrIdriveTest_usingCsv";
tm_9:
  testmethod_class = "ti_tml.ODP.XtrVtTest";

end
-----------------------------------------------------------------
test_suites

NULLDUT_1:
  local_flags = bypass, output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_lev_equ_set = 1;
  override_lev_spec_set = 12;
  override_levset = 2;
  override_seqlbl = "ODP_XTR_MPB";
  override_testf = tm_2;
  override_tim_spec_set = "pASYNC3_pNONASYNC1_ODP_MPT";
  override_timset = 1;
  site_control = "parallel:";
  site_match = 2;
ODP_IcapTest_st:
  local_flags = bypass, output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_lev_equ_set = 1;
  override_lev_spec_set = 12;
  override_levset = 2;
  override_seqlbl = "ODP_RO_MPB";
  override_testf = tm_10;
  override_tim_spec_set = "pASYNC2_pASYNC3_pNONASYNC1_WFT38_MPT";
  override_timset = 1;
  site_control = "parallel:";
  site_match = 2;
ODP_RingOscTest_st:
  local_flags = bypass, output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_lev_equ_set = 1;
  override_lev_spec_set = 12;
  override_levset = 2;
  override_seqlbl = "ODP_RO_MPB_x58";
  override_testf = tm_1;
  override_tim_spec_set = "pASYNC3_PASYNC5_PNONASYNC1_WFT9";
  override_timset = 1;
  site_control = "parallel:";
  site_match = 2;
XtrIdriveTest_1P5V_DUT:
  local_flags = bypass, output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_lev_equ_set = 1;
  override_lev_spec_set = 12;
  override_levset = 2;
  override_seqlbl = "ODP_XTR_MPB";
  override_testf = tm_6;
  override_tim_spec_set = "pASYNC3_pNONASYNC1_ODP_MPT";
  override_timset = 1;
  site_control = "parallel:";
  site_match = 2;
XtrIdriveTest_1P8V_DUT:
  local_flags = bypass, output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_lev_equ_set = 1;
  override_lev_spec_set = 12;
  override_levset = 2;
  override_seqlbl = "ODP_XTR_MPB";
  override_testf = tm_7;
  override_tim_spec_set = "pASYNC3_pNONASYNC1_ODP_MPT";
  override_timset = 1;
  site_control = "parallel:";
  site_match = 2;
XtrIdriveTest_CORE_HVT:
  local_flags = bypass, output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_lev_equ_set = 1;
  override_lev_spec_set = 12;
  override_levset = 2;
  override_seqlbl = "ODP_XTR_MPB";
  override_testf = tm_3;
  override_tim_spec_set = "pASYNC3_pNONASYNC1_ODP_MPT";
  override_timset = 1;
  site_control = "parallel:";
  site_match = 2;
XtrIdriveTest_CORE_LVT:
  local_flags = bypass, output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_lev_equ_set = 1;
  override_lev_spec_set = 12;
  override_levset = 2;
  override_seqlbl = "ODP_XTR_MPB";
  override_testf = tm_5;
  override_tim_spec_set = "pASYNC3_pNONASYNC1_ODP_MPT";
  override_timset = 1;
  site_control = "parallel:";
  site_match = 2;
XtrIdriveTest_CORE_SVT:
  local_flags = bypass, output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_lev_equ_set = 1;
  override_lev_spec_set = 12;
  override_levset = 2;
  override_seqlbl = "ODP_XTR_MPB";
  override_testf = tm_4;
  override_tim_spec_set = "pASYNC3_pNONASYNC1_ODP_MPT";
  override_timset = 1;
  site_control = "parallel:";
  site_match = 2;
XtrIdriveTest_SRAM:
  local_flags = bypass, output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_lev_equ_set = 1;
  override_lev_spec_set = 12;
  override_levset = 2;
  override_seqlbl = "ODP_XTR_MPB";
  override_testf = tm_8;
  override_tim_spec_set = "pASYNC3_pNONASYNC1_ODP_MPT";
  override_timset = 1;
  site_control = "parallel:";
  site_match = 2;
XtrVtTest:
  local_flags = bypass, output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_lev_equ_set = 1;
  override_lev_spec_set = 12;
  override_levset = 2;
  override_seqlbl = "ODP_XTR_MPB";
  override_testf = tm_9;
  override_tim_spec_set = "pASYNC3_pNONASYNC1_ODP_MPT";
  override_timset = 1;
  site_control = "parallel:";
  site_match = 2;

end
-----------------------------------------------------------------
test_flow

  {
    if @TITESTTYPE != "PB_RPC_LT" then
    {
       run_and_branch(ODP_RingOscTest_st)
       then
       {
       }
       else
       {
       }
       run_and_branch(NULLDUT_1)
       then
       {
       }
       else
       {
       }
       run_and_branch(XtrIdriveTest_CORE_HVT)
       then
       {
       }
       else
       {
       }
       run_and_branch(XtrIdriveTest_CORE_SVT)
       then
       {
       }
       else
       {
       }
       run_and_branch(XtrIdriveTest_CORE_LVT)
       then
       {
       }
       else
       {
       }
       run_and_branch(XtrIdriveTest_1P5V_DUT)
       then
       {
       }
       else
       {
       }
       run_and_branch(XtrIdriveTest_1P8V_DUT)
       then
       {
       }
       else
       {
       }
       run_and_branch(XtrIdriveTest_SRAM)
       then
       {
       }
       else
       {
       }
       run_and_branch(XtrVtTest)
       then
       {
       }
       else
       {
       }
       run_and_branch(ODP_IcapTest_st)
       then
       {
       }
       else
       {
       }
    }
    else
    {
    }

  },groupbypass, open,"ODP",""

end
-----------------------------------------------------------------
binning
end
-----------------------------------------------------------------
oocrule


end
-----------------------------------------------------------------
context


end
-----------------------------------------------------------------
hardware_bin_descriptions


end
-----------------------------------------------------------------
