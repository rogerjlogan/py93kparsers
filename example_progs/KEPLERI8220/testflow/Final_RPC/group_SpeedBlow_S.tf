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
tm_3:
  testmethod_class = "ti_tml.MCP.storeFmaxTFT";

end
-----------------------------------------------------------------
test_suites

ProgramVIDSpeeds:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_testf = tm_1;
  site_control = "parallel:";
  site_match = 2;
VerifyProgramVIDSpeeds:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_testf = tm_2;
  site_control = "parallel:";
  site_match = 2;
storeFmaxTFT:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_testf = tm_3;
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
    }
    run_and_branch(VerifyProgramVIDSpeeds)
    then
    {
    }
    else
    {
    }
    if @TITESTTYPE == "FT_RPC_HT" then
    {
       run_and_branch(storeFmaxTFT)
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
