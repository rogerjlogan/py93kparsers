hp93000,testflow,0.1
language_revision = 1;

testmethodparameters
end
-----------------------------------------------------------------
testmethodlimits
end
-----------------------------------------------------------------
testmethods

tm_1:
  testmethod_class = "ti_tml.MCP.MCP_ProgramVIDSpeeds";
tm_2:
  testmethod_class = "ti_tml.MCP.MCP_VerigyProgramVIDSpeeds";

end
-----------------------------------------------------------------
test_suites

ProgramVIDSpeeds:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_lev_equ_set = 1;
  override_lev_spec_set = 3;
  override_levset = 2;
  override_seqlbl = "Read_Norm_MPB";
  override_testf = tm_1;
  override_tim_spec_set = "efuse_Read_Program";
  override_timset = "1,1,1";
  site_control = "parallel:";
  site_match = 2;
VerifyProgramVIDSpeeds:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_lev_equ_set = 1;
  override_lev_spec_set = 4;
  override_levset = 2;
  override_seqlbl = "Read_Norm_MPB";
  override_testf = tm_2;
  override_tim_spec_set = "efuse_Read_Program";
  override_timset = "1,1,1";
  site_control = "parallel:";
  site_match = 2;

end
-----------------------------------------------------------------
test_flow

  {
    run_and_branch(ProgramVIDSpeeds)
    then
    {
    }
    else
    {
       multi_bin;
    }
    run_and_branch(VerifyProgramVIDSpeeds)
    then
    {
    }
    else
    {
       multi_bin;
    }

  },open,"SpeedBlow_S",""

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
