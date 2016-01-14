hp93000,testflow,0.1
language_revision = 1;

testmethodparameters

tm_1:
  "DigCapLabelName" = "CAP_ODP_RO_PMC_1";
  "GS70GROLabel" = "ODP_RO_MPB_x1";
  "GS70IROLabel" = "ODP_RO_MPB_x1_2";
  "InputDataPin" = "uart0rxd";
  "IsChar" = "0";
  "OutputDataPin" = "uart0txd";
  "TechName" = "SR80";
  "WfIndexForOne" = "0";
  "WfIndexForZero" = "1";
tm_2:
  "ForcePin" = "pmcforce0";
  "InputDataPin" = "uart0rxd";
  "SensePin" = "pmcsense0";
  "TechName" = "SR80";
  "WfIndexForOne" = "0";
  "WfIndexForZero" = "1";
tm_3:
  "CapTimingSpec" = "pASYNC1_pASYNC2_pNONASYNC1_WFT12_MPT";
  "CapacitanceLabel" = "ODP_ICAP_MPB";
  "DigCapLabelName" = "CAP_ODP_RO_PMC_1";
  "ForcePin" = "pmcforce0";
  "FreqTimingSpec" = "pASYNC1_pASYNC2_pNONASYNC1_WFT12_MPT";
  "FrequencyLabel" = "ODP_RO_MPB";
  "InputDataPin" = "uart0rxd";
  "IsChar" = "0";
  "OutputDataPin" = "uart0txd";
  "SensePin" = "pmcsense0";
  "TechName" = "SR80";
  "WfIndexForOne" = "0";
  "WfIndexForZero" = "1";
  "XtrVnom" = "0.85";
tm_4:
  "ForcePin" = "pmcforce0";
  "InputDataPin" = "uart0rxd";
  "IsChar" = "0";
  "SensePin" = "pmcsense0";
  "TechName" = "SR80";
  "WfIndexForOne" = "0";
  "WfIndexForZero" = "1";
  "XtrVnom" = "0.85";
tm_5:
  "ForcePin" = "pmcforce0";
  "InputDataPin" = "uart0rxd";
  "IsChar" = "0";
  "SR70ViaLabel" = "";
  "SR70XtrLabel" = "";
  "SensePin" = "pmcsense0";
  "TechName" = "SR80";
  "VTol" = "0.01";
  "WfIndexForOne" = "0";
  "WfIndexForZero" = "1";
tm_6:
  "ForcePin" = "pmcforce0";
  "InputDataPin" = "uart0rxd";
  "IsChar" = "0";
  "SensePin" = "pmcsense0";
  "TechName" = "SR80";
  "WfIndexForOne" = "0";
  "WfIndexForZero" = "1";
  "XtrVnom" = "0.85";

end
-----------------------------------------------------------------
testmethodlimits
end
-----------------------------------------------------------------
testmethods

tm_1:
  testmethod_class = "ti_tml.ODP.ODP_RingOscTest";
tm_2:
  testmethod_class = "ti_tml.ODP.ODP_NullDutTest";
tm_3:
  testmethod_class = "ti_tml.ODP.ODP_IcapTest";
tm_4:
  testmethod_class = "ti_tml.ODP.ODP_ViaTest";
tm_5:
  testmethod_class = "ti_tml.ODP.ODP_XtrIdriveTest";
tm_6:
  testmethod_class = "ti_tml.ODP.ODP_XtrVtTest";

end
-----------------------------------------------------------------
test_suites

ODP_IcapTest:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_lev_equ_set = 1;
  override_lev_spec_set = 15;
  override_levset = 2;
  override_seqlbl = "ODP_RO_MPB";
  override_testf = tm_3;
  override_tim_spec_set = "pASYNC1_pASYNC2_pNONASYNC1_WFT12_MPT";
  override_timset = 1;
  site_control = "parallel:";
  site_match = 2;
ODP_NullDutTest:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_lev_equ_set = 1;
  override_lev_spec_set = 15;
  override_levset = 2;
  override_seqlbl = "ODP_XTR_MPB";
  override_testf = tm_2;
  override_tim_spec_set = "pASYNC1_pASYNC2_pNONASYNC1_WFT12_MPT";
  override_timset = 1;
  site_control = "parallel:";
  site_match = 2;
ODP_RingOscTest:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_lev_equ_set = 1;
  override_lev_spec_set = 15;
  override_levset = 2;
  override_seqlbl = "ODP_RO_MPB";
  override_testf = tm_1;
  override_tim_spec_set = "pASYNC1_pASYNC2_pNONASYNC1_WFT12_MPT";
  override_timset = 1;
  site_control = "parallel:";
  site_match = 2;
ODP_ViaTest:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_lev_equ_set = 1;
  override_lev_spec_set = 15;
  override_levset = 2;
  override_seqlbl = "ODP_XTR_MPB";
  override_testf = tm_4;
  override_tim_spec_set = "pASYNC1_pASYNC2_pNONASYNC1_WFT12_MPT";
  override_timset = 1;
  site_control = "parallel:";
  site_match = 2;
ODP_XtrIdriveTest:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_lev_equ_set = 1;
  override_lev_spec_set = 15;
  override_levset = 2;
  override_seqlbl = "ODP_XTR_MPB";
  override_testf = tm_5;
  override_tim_spec_set = "pASYNC1_pASYNC2_pNONASYNC1_WFT12_MPT";
  override_timset = 1;
  site_control = "parallel:";
  site_match = 2;
ODP_XtrVtTest:
  local_flags = bypass, output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_lev_equ_set = 1;
  override_lev_spec_set = 15;
  override_levset = 2;
  override_seqlbl = "ODP_XTR_MPB";
  override_testf = tm_6;
  override_tim_spec_set = "pASYNC1_pASYNC2_pNONASYNC1_WFT12_MPT";
  override_timset = 1;
  site_control = "parallel:";
  site_match = 2;

end
-----------------------------------------------------------------
test_flow

  {
    run_and_branch(ODP_RingOscTest)
    then
    {
    }
    else
    {
    }
    run_and_branch(ODP_NullDutTest)
    then
    {
    }
    else
    {
    }
    run_and_branch(ODP_IcapTest)
    then
    {
    }
    else
    {
    }
    run_and_branch(ODP_ViaTest)
    then
    {
    }
    else
    {
    }
    run_and_branch(ODP_XtrIdriveTest)
    then
    {
    }
    else
    {
    }
    run_and_branch(ODP_XtrVtTest)
    then
    {
    }
    else
    {
    }

  },groupbypass, open,"OnDieStruc_S",""

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
