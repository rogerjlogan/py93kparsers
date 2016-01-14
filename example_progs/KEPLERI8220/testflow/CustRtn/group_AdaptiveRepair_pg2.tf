hp93000,testflow,0.1
language_revision = 1;

testmethodparameters

tm_2:
  "bistClk1Specs" = "freq@pASYNC1";
  "bistClk2Specs" = "freq@pASYNC3_nAlt, freq@pASYNC5";
  "coreOffsetSpecName" = "vddcore_vddsram_skew";
  "imageNums" = "100, 110";
  "numBistClks" = "2";
  "repCorners" = "VC_VminNSp, VC_VskewPhi";
  "vddRamSpecName" = "VDDRAM_PS";
  "voltageList" = ".765, .790,  .810";

end
-----------------------------------------------------------------
testmethodlimits
end
-----------------------------------------------------------------
testmethods

tm_1:
  testmethod_class = "miscellaneous_tml.TestControl.Disconnect";
tm_2:
  testmethod_class = "ti_tml.MemoryRepair.AdaptiveRepair";

end
-----------------------------------------------------------------
test_suites

AdaptiveRepair:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail, frg_single_shot;
  override = 1;
  override_lev_equ_set = 3;
  override_lev_spec_set = 1;
  override_levset = 2;
  override_seqlbl = "bnrgmxxxc1_1pr3xmxxxx_000_arp_MPB";
  override_testf = tm_2;
  override_tim_spec_set = "ADAPTIVE_REPAIR_pNONASYNC1_WFT14X4_MPT";
  override_timset = 1;
  site_control = "parallel:";
  site_match = 1;
DISCONNECT_1_1:
  local_flags = bypass, output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_testf = tm_1;
  site_control = "parallel:";
  site_match = 2;

end
-----------------------------------------------------------------
test_flow

  {
    if @TITESTTYPE == "FT_RPC_HT" then
    {
       run(DISCONNECT_1_1);
       run_and_branch(AdaptiveRepair)
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

  },open,"AdaptiveRepair",""

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
