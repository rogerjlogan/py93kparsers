hp93000,testflow,0.1
language_revision = 1;

testmethodparameters

tm_1:
  "AsyncClk" = "pLOAD";
  "Corner" = "Vmin";
  "Failed_labels_burst_name" = "";
  "Fmax_mult" = "1";
  "FreqStart" = "66";
  "FreqStep" = "1";
  "FreqStop" = "150";
  "Init_pattern" = "";
  "Interleave_init_pattern" = "No";
  "Limit_name" = "FBS_MA_LED_TETRIS";
  "PeriodSpec" = "per";
  "Pre/Post" = "Post";
  "Results_per_label" = "Yes";
  "Run_adaptive_search" = "No";
  "Run_stored_labels" = "No";
  "Stop_on_fail" = "No";
  "Store_failed_labels" = "No";
  "Stored_label_name" = "";
  "Warehouse_data_for_later_use" = "Yes";

end
-----------------------------------------------------------------
testmethodlimits


end
-----------------------------------------------------------------
testmethods

tm_1:
  testmethod_class = "ti_tml.Digital.Fmax";

end
-----------------------------------------------------------------
test_suites

LED_TETRIS_FreqSearch_st:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_lev_equ_set = 1;
  override_lev_spec_set = 9;
  override_levset = 2;
  override_seqlbl = "LED_TETRIS_MPB";
  override_testf = tm_1;
  override_tim_spec_set = "pLOAD_pNOLOAD_pASYNC3_pASYNC4_pASYNC5_WFT5X8_4_MPT";
  override_timset = 1;
  site_control = "parallel:";
  site_match = 2;

end
-----------------------------------------------------------------
test_flow
  {
    run_and_branch(LED_TETRIS_FreqSearch_st)
    then
    {
    }
    else
    {
       multi_bin;
    }
  },open,"FmaxSearch_S",""

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
