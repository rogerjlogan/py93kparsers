hp93000,testflow,0.1
language_revision = 1;

testmethodparameters

tm_4:
  "DPS_disconnect_pinlist" = "";
  "DPS_setVoltages" = "0.0115,0.0115,0.0115,0.0115,0.0115,0.0115,0.0115,0.0115,0.0115,0.0115,0.0115,0.0115";
  "Limit_names" = "I_A_SP_VDDDDR,I_A_SP_VDDPLL,I_A_SP_VDDIO,I_A_SP_VDDNWA,I_A_SP_VDDPLL,I_A_SP_VDDRAM,I_A_SP_VDDSHI,I_A_SP_VDDSLO,I_A_SP_VDDUHI,I_A_SP_VDDULO,I_A_SP_VPP,I_A_SP_VDDCORE";
  "Perform_functional_pretest" = "No";
  "Pins" = "VDDDDR,VDDDPLL,VDDIO,VDDNWA,VDDPLL,VDDRAM,VDDSHI,VDDSLO,VDDUHI,VDDULO,VPP,VDDCORE";
  "Power_of_2_number_of_samples" = "16";
  "Wait_time_ms" = "35";

end
-----------------------------------------------------------------
testmethodlimits
end
-----------------------------------------------------------------
testmethods

tm_1:
  testmethod_class = "miscellaneous_tml.TestControl.Disconnect";
tm_2:
  testmethod_class = "ti_tml.BBT.CheckOverTempFlag";
tm_3:
  testmethod_class = "miscellaneous_tml.TestControl.Disconnect";
tm_4:
  testmethod_class = "ti_tml.DC.Supply_shorts";
tm_5:
  testmethod_class = "ti_tml.Misc.BinningDieID";
tm_6:
  testmethod_class = "miscellaneous_tml.TestControl.Disconnect";

end
-----------------------------------------------------------------
test_suites

BBT_Status:
  local_flags = bypass, output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail, frg_single_shot;
  override = 1;
  override_lev_equ_set = 1;
  override_lev_spec_set = 11;
  override_levset = 2;
  override_seqlbl = "BBT_read_mpb";
  override_testf = tm_2;
  override_tim_spec_set = "bbtSpec";
  override_timset = 1;
  site_control = "parallel:";
  site_match = 2;
DISCONNECT_1:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_testf = tm_3;
  site_control = "parallel:";
  site_match = 2;
DISCONNECT_1_2:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_testf = tm_1;
  site_control = "parallel:";
  site_match = 2;
DISCONNECT_AtEndOfFlow:
  local_flags = bypass, output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_testf = tm_6;
  site_control = "parallel:";
  site_match = 2;
SortUnits:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_testf = tm_5;
  site_control = "parallel:";
  site_match = 2;
SupplyShortsPost_st:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_lev_equ_set = 2;
  override_lev_spec_set = 2;
  override_levset = 2;
  override_testf = tm_4;
  override_tim_spec_set = "pALL_PLUS_DPS_WFT1_MPT";
  override_timset = 1;
  site_control = "parallel:";
  site_match = 2;

end
-----------------------------------------------------------------
test_flow

  {
    run(DISCONNECT_1_2);
    {
       run(BBT_Status);
    }, open, "BBTStatusBypass", ""
    run(DISCONNECT_1);
    run_and_branch(SupplyShortsPost_st)
    then
    {
    }
    else
    {
       multi_bin;
    }
    run(SortUnits);
    multi_bin;
    run(DISCONNECT_AtEndOfFlow);

  },open,"SupplyShortsPost_S",""

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
