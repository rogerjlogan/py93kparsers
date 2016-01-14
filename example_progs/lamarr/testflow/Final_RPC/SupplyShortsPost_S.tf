hp93000,testflow,0.1
language_revision = 1;

testmethodparameters

tm_2:
  "DPS_disconnect_pinlist" = "";
  "DPS_setVoltages" = "0.025,0.025,0.025,0.025,0.025,0.025,0.025,0.025,0.025,0.025,0.025,0.025";
  "Limit_names" = "I_A_SP_VDDCORE,I_A_SP_VDDUHI,I_A_SP_VDDSLO,I_A_SP_VDDRAM,I_A_SP_VDDSHI,I_A_SP_VDDDPLL,I_A_SP_VDDDDR,I_A_SP_VDDIO,I_A_SP_VDDULO,I_A_SP_VDDNWA,I_A_SP_VPP,I_A_SP_VDDPLL";
  "Perform_functional_pretest" = "No";
  "Pins" = "VDDCORE,VDDUHI,VDDSLO,VDDRAM,VDDSHI,VDDDPLL,VDDDDR,VDDIO,VDDULO,VDDNWA,VPP,VDDPLL";
  "PowerDown_wait_ms" = "10";
  "Power_of_2_number_of_samples" = "2048";
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
  testmethod_class = "ti_tml.DC.Supply_shorts";

end
-----------------------------------------------------------------
test_suites

DISCONNECT_SupplyShortsPost:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_testf = tm_1;
  site_control = "parallel:";
  site_match = 2;
SupplyShortsPost_st:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_lev_equ_set = 2;
  override_lev_spec_set = 1;
  override_levset = 1;
  override_seqlbl = "";
  override_testf = tm_2;
  override_tim_spec_set = "pALL_PLUS_DPS_WFT2_MPT";
  override_timset = "1";
  site_control = "parallel:";
  site_match = 2;

end
-----------------------------------------------------------------
test_flow

  {
    run(DISCONNECT_SupplyShortsPost);
    run_and_branch(SupplyShortsPost_st)
    then
    {
    }
    else
    {
       multi_bin;
    }

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
