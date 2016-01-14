hp93000,testflow,0.1
language_revision = 1;

testmethodparameters

tm_1:
  "Auto Tune PID temperature" = "0";
  "Control Temperature" = "0";
  "Enable Cooling" = "0";
  "Enable Heating" = "0";
  "End Of Flow Warm Up Time Out" = "15";
  "Lower Limit Range Offset Temperature" = "0";
  "Pattern name to cool down device" = "dummy_pNONASYNC1_MP";
  "Pattern name to warm up device" = "PB_PLL_S1R_T0_1_PG_ASV_MPB";
  "SPT OFFSET" = "0";
  "Thermo Control Mode" = "WARMUP";
  "Time Between TD Reading" = "1";
  "Upper Limit Range Offset Temperature" = "0";
  "WarmUpLevelsCorner" = "VmaxTHAW";
  "WarmUpLevelset" = "2";
  "WarmUpTimingSet" = "1";
  "WarmUpTimingSpecName" = "PBIST_pASYNC2_pASYNC3_pNONASYNC1_WFT11X4_MPT_1214";

end
-----------------------------------------------------------------
testmethodlimits
end
-----------------------------------------------------------------
testmethods

tm_1:
  testmethod_class = "ti_tml.Thermal.Thermal_Control";

end
-----------------------------------------------------------------
test_suites

EndOfFlowThaw:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_lev_equ_set = 1;
  override_lev_spec_set = 35;
  override_levset = 2;
  override_seqlbl = "PB_PLL_S1R_T0_1_PG_ASV_MPB";
  override_testf = tm_1;
  override_tim_spec_set = "PBIST_pASYNC2_pASYNC3_pNONASYNC1_WFT11X4_MPT_1214";
  override_timset = 1;
  site_control = "parallel:";
  site_match = 2;

end
-----------------------------------------------------------------
test_flow

  {
    if @TITESTTYPE == "PB_RPC_LT" then
    {
       run_and_branch(EndOfFlowThaw)
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

  },open,"ColdTempTHAW",""

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
