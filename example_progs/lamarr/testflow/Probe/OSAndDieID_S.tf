hp93000,testflow,0.1
language_revision = 1;

testmethodparameters

tm_1:
  "Limit_names" = "I_B_OPEN_PINS";
  "Pins" = "OPEN_PINS";
  "SettlingTime_ms" = "1";
  "TestCurrent_uA" = "10";
  "Util_purpose_off" = "";
  "Util_purpose_on" = "";
tm_2:
  "Limit_names" = "I_B_OPEN_PINS";
  "Pins" = "OPEN_PINS";
  "SettlingTime_ms" = "1";
  "TestCurrent_uA" = "10";
  "Util_purpose_off" = "";
  "Util_purpose_on" = "";

end
-----------------------------------------------------------------
testmethodlimits


end
-----------------------------------------------------------------
testmethods

tm_1:
  testmethod_class = "ti_tml.DC.Continuity_opens";
tm_2:
  testmethod_class = "ti_tml.DC.Continuity_opens";

end
-----------------------------------------------------------------
test_suites

PinOpensTest_st:
  local_flags = output_on_pass, output_on_fail;
  override = 1;
  override_lev_equ_set = 1;
  override_lev_spec_set = 1;
  override_levset = 1;
  override_seqlbl = "";
  override_testf = tm_1;
  override_tim_equ_set = 1;
  override_tim_spec_set = 1;
  override_timset = 1;
  site_control = "parallel:";
  site_match = 2;
PinOpensTestPerPin_st:
  local_flags = output_on_pass, output_on_fail;
  override = 1;
  override_lev_equ_set = 1;
  override_lev_spec_set = 1;
  override_levset = 1;
  override_seqlbl = "";
  override_testf = tm_2;
  override_tim_equ_set = 1;
  override_tim_spec_set = 1;
  override_timset = 1;
  site_control = "parallel:";
  site_match = 2;

end
-----------------------------------------------------------------
test_flow
  {
    run_and_branch(PinOpensTest_st)
    then
    {
    }
    else
    {
       run_and_branch(PinOpensTestPerPin_st)
       then
       {
       }
       else
       {
          multi_bin;
       }
    }
  },open,"OSAndDieID_S",""

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
