\ Model Grid_Transformation
\ LP format - for model browsing. Use MPS format to capture full model detail.
Minimize
  5 x_flow_Methane_S1_D1 + 5 y_new_capMethane_S1_D1 + 8 x_flow_Methane_S1_D2
   + 5 y_new_capMethane_S1_D2 + 6 x_flow_Methane_S2_D2
   + 5 y_new_capMethane_S2_D2 + 10 x_flow_Methane_S2_D3
   + 5 y_new_capMethane_S2_D3 + 7 x_flow_Methane_S3_D1
   + 5 y_new_capMethane_S3_D1 + 3 x_flow_Methane_D1_D2
   + 5 y_new_capMethane_D1_D2 + x_flow_Methane_D3_D4
   + 5 y_new_capMethane_D3_D4 + 2 x_flow_Methane_D4_D5
   + 5 y_new_capMethane_D4_D5 + 3 x_flow_Methane_D4_D6
   + 5 y_new_capMethane_D4_D6 + 5 x_flow_Methane_D6_D7
   + 5 y_new_capMethane_D6_D7 + 4 x_flow_Methane_D5_D8
   + 5 y_new_capMethane_D5_D8 + 7 x_flow_Methane_D5_D9
   + 5 y_new_capMethane_D5_D9 + 5 x_flow_Methane_D9_D10
   + 5 y_new_capMethane_D9_D10 + 2 x_flow_Methane_D7_D10
   + 5 y_new_capMethane_D7_D10 + 0 y_new_capMethane_shortage_S1_S1
   + 0 z_conv_capMethane_shortage_S1_S1 + 0 change_Methane_shortage_S1_S1
   + 0 y_new_capMethane_shortage_S2_S2 + 0 z_conv_capMethane_shortage_S2_S2
   + 0 change_Methane_shortage_S2_S2 + 0 y_new_capMethane_shortage_S3_S3
   + 0 z_conv_capMethane_shortage_S3_S3 + 0 change_Methane_shortage_S3_S3
   + 0 x_flow_shortage_Methane_shortage_S1_S1
   + 0 x_flow_shortage_Methane_shortage_S2_S2
   + 0 x_flow_shortage_Methane_shortage_S3_S3 + 5 x_flow_Hydrogen_S1_D1
   + 12 y_new_capHydrogen_S1_D1 + 0.5 z_conv_capHydrogen_S1_D1
   + 8 x_flow_Hydrogen_S1_D2 + 12 y_new_capHydrogen_S1_D2
   + 0.5 z_conv_capHydrogen_S1_D2 + 6 x_flow_Hydrogen_S2_D2
   + 12 y_new_capHydrogen_S2_D2 + 0.5 z_conv_capHydrogen_S2_D2
   + 10 x_flow_Hydrogen_S2_D3 + 12 y_new_capHydrogen_S2_D3
   + 0.5 z_conv_capHydrogen_S2_D3 + 7 x_flow_Hydrogen_S3_D1
   + 12 y_new_capHydrogen_S3_D1 + 0.5 z_conv_capHydrogen_S3_D1
   + 3 x_flow_Hydrogen_D1_D2 + 12 y_new_capHydrogen_D1_D2
   + 0.5 z_conv_capHydrogen_D1_D2 + x_flow_Hydrogen_D3_D4
   + 12 y_new_capHydrogen_D3_D4 + 0.5 z_conv_capHydrogen_D3_D4
   + 2 x_flow_Hydrogen_D4_D5 + 12 y_new_capHydrogen_D4_D5
   + 0.5 z_conv_capHydrogen_D4_D5 + 3 x_flow_Hydrogen_D4_D6
   + 12 y_new_capHydrogen_D4_D6 + 0.5 z_conv_capHydrogen_D4_D6
   + 5 x_flow_Hydrogen_D6_D7 + 12 y_new_capHydrogen_D6_D7
   + 0.5 z_conv_capHydrogen_D6_D7 + 4 x_flow_Hydrogen_D5_D8
   + 12 y_new_capHydrogen_D5_D8 + 0.5 z_conv_capHydrogen_D5_D8
   + 7 x_flow_Hydrogen_D5_D9 + 12 y_new_capHydrogen_D5_D9
   + 0.5 z_conv_capHydrogen_D5_D9 + 5 x_flow_Hydrogen_D9_D10
   + 12 y_new_capHydrogen_D9_D10 + 0.5 z_conv_capHydrogen_D9_D10
   + 2 x_flow_Hydrogen_D7_D10 + 12 y_new_capHydrogen_D7_D10
   + 0.5 z_conv_capHydrogen_D7_D10 + 0 y_new_capHydrogen_shortage_S1_S1
   + 0 z_conv_capHydrogen_shortage_S1_S1 + 0 change_Hydrogen_shortage_S1_S1
   + 0 y_new_capHydrogen_shortage_S2_S2
   + 0 z_conv_capHydrogen_shortage_S2_S2 + 0 change_Hydrogen_shortage_S2_S2
   + 0 y_new_capHydrogen_shortage_S3_S3
   + 0 z_conv_capHydrogen_shortage_S3_S3 + 0 change_Hydrogen_shortage_S3_S3
   + 0 x_flow_shortage_Hydrogen_shortage_S1_S1
   + 0 x_flow_shortage_Hydrogen_shortage_S2_S2
   + 0 x_flow_shortage_Hydrogen_shortage_S3_S3
Subject To
 flow_constraint_Methane_S1: - x_flow_Methane_S1_D1 - x_flow_Methane_S1_D2
   = -20
 flow_constraint_Hydrogen_S1: - x_flow_Hydrogen_S1_D1
   - x_flow_Hydrogen_S1_D2 = -20
 flow_constraint_Methane_S2: - x_flow_Methane_S2_D2 - x_flow_Methane_S2_D3
   = -81
 flow_constraint_Hydrogen_S2: - x_flow_Hydrogen_S2_D2
   - x_flow_Hydrogen_S2_D3 = -81
 flow_constraint_Methane_S3: - x_flow_Methane_S3_D1 = -15
 flow_constraint_Hydrogen_S3: - x_flow_Hydrogen_S3_D1 = -15
 flow_constraint_Methane_D1: x_flow_Methane_S1_D1 + x_flow_Methane_S3_D1
   - x_flow_Methane_D1_D2 = 15
 flow_constraint_Hydrogen_D1: x_flow_Hydrogen_S1_D1 + x_flow_Hydrogen_S3_D1
   - x_flow_Hydrogen_D1_D2 = 15
 flow_constraint_Methane_D2: x_flow_Methane_S1_D2 + x_flow_Methane_S2_D2
   + x_flow_Methane_D1_D2 = 20
 flow_constraint_Hydrogen_D2: x_flow_Hydrogen_S1_D2 + x_flow_Hydrogen_S2_D2
   + x_flow_Hydrogen_D1_D2 = 20
 flow_constraint_Methane_D3: x_flow_Methane_S2_D3 - x_flow_Methane_D3_D4
   = 25
 flow_constraint_Hydrogen_D3: x_flow_Hydrogen_S2_D3 - x_flow_Hydrogen_D3_D4
   = 25
 flow_constraint_Methane_D4: x_flow_Methane_D3_D4 - x_flow_Methane_D4_D5
   - x_flow_Methane_D4_D6 = 1
 flow_constraint_Hydrogen_D4: x_flow_Hydrogen_D3_D4 - x_flow_Hydrogen_D4_D5
   - x_flow_Hydrogen_D4_D6 = 1
 flow_constraint_Methane_D5: x_flow_Methane_D4_D5 - x_flow_Methane_D5_D8
   - x_flow_Methane_D5_D9 = 20
 flow_constraint_Hydrogen_D5: x_flow_Hydrogen_D4_D5 - x_flow_Hydrogen_D5_D8
   - x_flow_Hydrogen_D5_D9 = 20
 flow_constraint_Methane_D6: x_flow_Methane_D4_D6 - x_flow_Methane_D6_D7
   = 5
 flow_constraint_Hydrogen_D6: x_flow_Hydrogen_D4_D6 - x_flow_Hydrogen_D6_D7
   = 5
 flow_constraint_Methane_D7: x_flow_Methane_D6_D7 - x_flow_Methane_D7_D10
   = 5
 flow_constraint_Hydrogen_D7: x_flow_Hydrogen_D6_D7
   - x_flow_Hydrogen_D7_D10 = 5
 flow_constraint_Methane_D8: x_flow_Methane_D5_D8 = 10
 flow_constraint_Hydrogen_D8: x_flow_Hydrogen_D5_D8 = 10
 flow_constraint_Methane_D9: x_flow_Methane_D5_D9 - x_flow_Methane_D9_D10
   = 10
 flow_constraint_Hydrogen_D9: x_flow_Hydrogen_D5_D9
   - x_flow_Hydrogen_D9_D10 = 10
 flow_constraint_Methane_D10: x_flow_Methane_D9_D10 + x_flow_Methane_D7_D10
   = 5
 flow_constraint_Hydrogen_D10: x_flow_Hydrogen_D9_D10
   + x_flow_Hydrogen_D7_D10 = 5
 supply_shortage_Methane_shortage_S1: - x_flow_Methane_shortage_S1_S1 >= 0
 supply_shortage_Hydrogen_shortage_S1: - x_flow_Hydrogen_shortage_S1_S1
   >= 0
 supply_shortage_Methane_shortage_S2: - x_flow_Methane_shortage_S2_S2 >= 0
 supply_shortage_Hydrogen_shortage_S2: - x_flow_Hydrogen_shortage_S2_S2
   >= 0
 supply_shortage_Methane_shortage_S3: - x_flow_Methane_shortage_S3_S3 >= 0
 supply_shortage_Hydrogen_shortage_S3: - x_flow_Hydrogen_shortage_S3_S3
   >= 0
 used_capacity_Methane_S1_D1: x_flow_Methane_S1_D1 - y_new_capMethane_S1_D1
   - z_conv_capMethane_S1_D1 <= 0
 used_capacity_Methane_S1_D2: x_flow_Methane_S1_D2 - y_new_capMethane_S1_D2
   - z_conv_capMethane_S1_D2 <= 0
 used_capacity_Methane_S2_D2: x_flow_Methane_S2_D2 - y_new_capMethane_S2_D2
   - z_conv_capMethane_S2_D2 <= 0
 used_capacity_Methane_S2_D3: x_flow_Methane_S2_D3 - y_new_capMethane_S2_D3
   - z_conv_capMethane_S2_D3 <= 0
 used_capacity_Methane_S3_D1: x_flow_Methane_S3_D1 - y_new_capMethane_S3_D1
   - z_conv_capMethane_S3_D1 <= 0
 used_capacity_Methane_D1_D2: x_flow_Methane_D1_D2 - y_new_capMethane_D1_D2
   - z_conv_capMethane_D1_D2 <= 0
 used_capacity_Methane_D3_D4: x_flow_Methane_D3_D4 - y_new_capMethane_D3_D4
   - z_conv_capMethane_D3_D4 <= 0
 used_capacity_Methane_D4_D5: x_flow_Methane_D4_D5 - y_new_capMethane_D4_D5
   - z_conv_capMethane_D4_D5 <= 0
 used_capacity_Methane_D4_D6: x_flow_Methane_D4_D6 - y_new_capMethane_D4_D6
   - z_conv_capMethane_D4_D6 <= 0
 used_capacity_Methane_D6_D7: x_flow_Methane_D6_D7 - y_new_capMethane_D6_D7
   - z_conv_capMethane_D6_D7 <= 0
 used_capacity_Methane_D5_D8: x_flow_Methane_D5_D8 - y_new_capMethane_D5_D8
   - z_conv_capMethane_D5_D8 <= 0
 used_capacity_Methane_D5_D9: x_flow_Methane_D5_D9 - y_new_capMethane_D5_D9
   - z_conv_capMethane_D5_D9 <= 0
 used_capacity_Methane_D9_D10: x_flow_Methane_D9_D10
   - y_new_capMethane_D9_D10 - z_conv_capMethane_D9_D10 <= 0
 used_capacity_Methane_D7_D10: x_flow_Methane_D7_D10
   - y_new_capMethane_D7_D10 - z_conv_capMethane_D7_D10 <= 0
 used_capacity_Hydrogen_S1_D1: x_flow_Hydrogen_S1_D1
   - y_new_capHydrogen_S1_D1 - z_conv_capHydrogen_S1_D1 <= 0
 used_capacity_Hydrogen_S1_D2: x_flow_Hydrogen_S1_D2
   - y_new_capHydrogen_S1_D2 - z_conv_capHydrogen_S1_D2 <= 0
 used_capacity_Hydrogen_S2_D2: x_flow_Hydrogen_S2_D2
   - y_new_capHydrogen_S2_D2 - z_conv_capHydrogen_S2_D2 <= 0
 used_capacity_Hydrogen_S2_D3: x_flow_Hydrogen_S2_D3
   - y_new_capHydrogen_S2_D3 - z_conv_capHydrogen_S2_D3 <= 0
 used_capacity_Hydrogen_S3_D1: x_flow_Hydrogen_S3_D1
   - y_new_capHydrogen_S3_D1 - z_conv_capHydrogen_S3_D1 <= 0
 used_capacity_Hydrogen_D1_D2: x_flow_Hydrogen_D1_D2
   - y_new_capHydrogen_D1_D2 - z_conv_capHydrogen_D1_D2 <= 0
 used_capacity_Hydrogen_D3_D4: x_flow_Hydrogen_D3_D4
   - y_new_capHydrogen_D3_D4 - z_conv_capHydrogen_D3_D4 <= 0
 used_capacity_Hydrogen_D4_D5: x_flow_Hydrogen_D4_D5
   - y_new_capHydrogen_D4_D5 - z_conv_capHydrogen_D4_D5 <= 0
 used_capacity_Hydrogen_D4_D6: x_flow_Hydrogen_D4_D6
   - y_new_capHydrogen_D4_D6 - z_conv_capHydrogen_D4_D6 <= 0
 used_capacity_Hydrogen_D6_D7: x_flow_Hydrogen_D6_D7
   - y_new_capHydrogen_D6_D7 - z_conv_capHydrogen_D6_D7 <= 0
 used_capacity_Hydrogen_D5_D8: x_flow_Hydrogen_D5_D8
   - y_new_capHydrogen_D5_D8 - z_conv_capHydrogen_D5_D8 <= 0
 used_capacity_Hydrogen_D5_D9: x_flow_Hydrogen_D5_D9
   - y_new_capHydrogen_D5_D9 - z_conv_capHydrogen_D5_D9 <= 0
 used_capacity_Hydrogen_D9_D10: x_flow_Hydrogen_D9_D10
   - y_new_capHydrogen_D9_D10 - z_conv_capHydrogen_D9_D10 <= 0
 used_capacity_Hydrogen_D7_D10: x_flow_Hydrogen_D7_D10
   - y_new_capHydrogen_D7_D10 - z_conv_capHydrogen_D7_D10 <= 0
 capacity_Methane_S1_D1: y_new_capMethane_S1_D1 + z_conv_capMethane_S1_D1
   <= 500
 capacity_Methane_S1_D2: y_new_capMethane_S1_D2 + z_conv_capMethane_S1_D2
   <= 500
 capacity_Methane_S2_D2: y_new_capMethane_S2_D2 + z_conv_capMethane_S2_D2
   <= 500
 capacity_Methane_S2_D3: y_new_capMethane_S2_D3 + z_conv_capMethane_S2_D3
   <= 500
 capacity_Methane_S3_D1: y_new_capMethane_S3_D1 + z_conv_capMethane_S3_D1
   <= 500
 capacity_Methane_D1_D2: y_new_capMethane_D1_D2 + z_conv_capMethane_D1_D2
   <= 500
 capacity_Methane_D3_D4: y_new_capMethane_D3_D4 + z_conv_capMethane_D3_D4
   <= 500
 capacity_Methane_D4_D5: y_new_capMethane_D4_D5 + z_conv_capMethane_D4_D5
   <= 500
 capacity_Methane_D4_D6: y_new_capMethane_D4_D6 + z_conv_capMethane_D4_D6
   <= 500
 capacity_Methane_D6_D7: y_new_capMethane_D6_D7 + z_conv_capMethane_D6_D7
   <= 500
 capacity_Methane_D5_D8: y_new_capMethane_D5_D8 + z_conv_capMethane_D5_D8
   <= 500
 capacity_Methane_D5_D9: y_new_capMethane_D5_D9 + z_conv_capMethane_D5_D9
   <= 500
 capacity_Methane_D9_D10: y_new_capMethane_D9_D10
   + z_conv_capMethane_D9_D10 <= 500
 capacity_Methane_D7_D10: y_new_capMethane_D7_D10
   + z_conv_capMethane_D7_D10 <= 500
 capacity_Hydrogen_S1_D1: y_new_capHydrogen_S1_D1
   + z_conv_capHydrogen_S1_D1 <= 500
 capacity_Hydrogen_S1_D2: y_new_capHydrogen_S1_D2
   + z_conv_capHydrogen_S1_D2 <= 500
 capacity_Hydrogen_S2_D2: y_new_capHydrogen_S2_D2
   + z_conv_capHydrogen_S2_D2 <= 500
 capacity_Hydrogen_S2_D3: y_new_capHydrogen_S2_D3
   + z_conv_capHydrogen_S2_D3 <= 500
 capacity_Hydrogen_S3_D1: y_new_capHydrogen_S3_D1
   + z_conv_capHydrogen_S3_D1 <= 500
 capacity_Hydrogen_D1_D2: y_new_capHydrogen_D1_D2
   + z_conv_capHydrogen_D1_D2 <= 500
 capacity_Hydrogen_D3_D4: y_new_capHydrogen_D3_D4
   + z_conv_capHydrogen_D3_D4 <= 500
 capacity_Hydrogen_D4_D5: y_new_capHydrogen_D4_D5
   + z_conv_capHydrogen_D4_D5 <= 500
 capacity_Hydrogen_D4_D6: y_new_capHydrogen_D4_D6
   + z_conv_capHydrogen_D4_D6 <= 500
 capacity_Hydrogen_D6_D7: y_new_capHydrogen_D6_D7
   + z_conv_capHydrogen_D6_D7 <= 500
 capacity_Hydrogen_D5_D8: y_new_capHydrogen_D5_D8
   + z_conv_capHydrogen_D5_D8 <= 500
 capacity_Hydrogen_D5_D9: y_new_capHydrogen_D5_D9
   + z_conv_capHydrogen_D5_D9 <= 500
 capacity_Hydrogen_D9_D10: y_new_capHydrogen_D9_D10
   + z_conv_capHydrogen_D9_D10 <= 500
 capacity_Hydrogen_D7_D10: y_new_capHydrogen_D7_D10
   + z_conv_capHydrogen_D7_D10 <= 500
 switching_constraint_S1_D1: change_Methane_S1_D1 + change_Hydrogen_S1_D1
   = 1
 switching_constraint_S1_D2: change_Methane_S1_D2 + change_Hydrogen_S1_D2
   = 1
 switching_constraint_S2_D2: change_Methane_S2_D2 + change_Hydrogen_S2_D2
   = 1
 switching_constraint_S2_D3: change_Methane_S2_D3 + change_Hydrogen_S2_D3
   = 1
 switching_constraint_S3_D1: change_Methane_S3_D1 + change_Hydrogen_S3_D1
   = 1
 switching_constraint_D1_D2: change_Methane_D1_D2 + change_Hydrogen_D1_D2
   = 1
 switching_constraint_D3_D4: change_Methane_D3_D4 + change_Hydrogen_D3_D4
   = 1
 switching_constraint_D4_D5: change_Methane_D4_D5 + change_Hydrogen_D4_D5
   = 1
 switching_constraint_D4_D6: change_Methane_D4_D6 + change_Hydrogen_D4_D6
   = 1
 switching_constraint_D6_D7: change_Methane_D6_D7 + change_Hydrogen_D6_D7
   = 1
 switching_constraint_D5_D8: change_Methane_D5_D8 + change_Hydrogen_D5_D8
   = 1
 switching_constraint_D5_D9: change_Methane_D5_D9 + change_Hydrogen_D5_D9
   = 1
 switching_constraint_D9_D10: change_Methane_D9_D10
   + change_Hydrogen_D9_D10 = 1
 switching_constraint_D7_D10: change_Methane_D7_D10
   + change_Hydrogen_D7_D10 = 1
 changed_capacity_Methane_S1_D1: - z_conv_capMethane_S1_D1
   + 500 change_Methane_S1_D1 = 0
 changed_capacity_Methane_S1_D2: - z_conv_capMethane_S1_D2
   + 500 change_Methane_S1_D2 = 0
 changed_capacity_Methane_S2_D2: - z_conv_capMethane_S2_D2
   + 500 change_Methane_S2_D2 = 0
 changed_capacity_Methane_S2_D3: - z_conv_capMethane_S2_D3
   + 500 change_Methane_S2_D3 = 0
 changed_capacity_Methane_S3_D1: - z_conv_capMethane_S3_D1
   + 500 change_Methane_S3_D1 = 0
 changed_capacity_Methane_D1_D2: - z_conv_capMethane_D1_D2
   + 500 change_Methane_D1_D2 = 0
 changed_capacity_Methane_D3_D4: - z_conv_capMethane_D3_D4
   + 500 change_Methane_D3_D4 = 0
 changed_capacity_Methane_D4_D5: - z_conv_capMethane_D4_D5
   + 500 change_Methane_D4_D5 = 0
 changed_capacity_Methane_D4_D6: - z_conv_capMethane_D4_D6
   + 500 change_Methane_D4_D6 = 0
 changed_capacity_Methane_D6_D7: - z_conv_capMethane_D6_D7
   + 500 change_Methane_D6_D7 = 0
 changed_capacity_Methane_D5_D8: - z_conv_capMethane_D5_D8
   + 500 change_Methane_D5_D8 = 0
 changed_capacity_Methane_D5_D9: - z_conv_capMethane_D5_D9
   + 500 change_Methane_D5_D9 = 0
 changed_capacity_Methane_D9_D10: - z_conv_capMethane_D9_D10
   + 500 change_Methane_D9_D10 = 0
 changed_capacity_Methane_D7_D10: - z_conv_capMethane_D7_D10
   + 500 change_Methane_D7_D10 = 0
 changed_capacity_Hydrogen_S1_D1: - z_conv_capHydrogen_S1_D1
   + 500 change_Hydrogen_S1_D1 = 0
 changed_capacity_Hydrogen_S1_D2: - z_conv_capHydrogen_S1_D2
   + 500 change_Hydrogen_S1_D2 = 0
 changed_capacity_Hydrogen_S2_D2: - z_conv_capHydrogen_S2_D2
   + 500 change_Hydrogen_S2_D2 = 0
 changed_capacity_Hydrogen_S2_D3: - z_conv_capHydrogen_S2_D3
   + 500 change_Hydrogen_S2_D3 = 0
 changed_capacity_Hydrogen_S3_D1: - z_conv_capHydrogen_S3_D1
   + 500 change_Hydrogen_S3_D1 = 0
 changed_capacity_Hydrogen_D1_D2: - z_conv_capHydrogen_D1_D2
   + 500 change_Hydrogen_D1_D2 = 0
 changed_capacity_Hydrogen_D3_D4: - z_conv_capHydrogen_D3_D4
   + 500 change_Hydrogen_D3_D4 = 0
 changed_capacity_Hydrogen_D4_D5: - z_conv_capHydrogen_D4_D5
   + 500 change_Hydrogen_D4_D5 = 0
 changed_capacity_Hydrogen_D4_D6: - z_conv_capHydrogen_D4_D6
   + 500 change_Hydrogen_D4_D6 = 0
 changed_capacity_Hydrogen_D6_D7: - z_conv_capHydrogen_D6_D7
   + 500 change_Hydrogen_D6_D7 = 0
 changed_capacity_Hydrogen_D5_D8: - z_conv_capHydrogen_D5_D8
   + 500 change_Hydrogen_D5_D8 = 0
 changed_capacity_Hydrogen_D5_D9: - z_conv_capHydrogen_D5_D9
   + 500 change_Hydrogen_D5_D9 = 0
 changed_capacity_Hydrogen_D9_D10: - z_conv_capHydrogen_D9_D10
   + 500 change_Hydrogen_D9_D10 = 0
 changed_capacity_Hydrogen_D7_D10: - z_conv_capHydrogen_D7_D10
   + 500 change_Hydrogen_D7_D10 = 0
 non_negativity_x_Methane_S1_D1: x_flow_Methane_S1_D1 >= 0
 non_negativity_x_Methane_S1_D2: x_flow_Methane_S1_D2 >= 0
 non_negativity_x_Methane_S2_D2: x_flow_Methane_S2_D2 >= 0
 non_negativity_x_Methane_S2_D3: x_flow_Methane_S2_D3 >= 0
 non_negativity_x_Methane_S3_D1: x_flow_Methane_S3_D1 >= 0
 non_negativity_x_Methane_D1_D2: x_flow_Methane_D1_D2 >= 0
 non_negativity_x_Methane_D3_D4: x_flow_Methane_D3_D4 >= 0
 non_negativity_x_Methane_D4_D5: x_flow_Methane_D4_D5 >= 0
 non_negativity_x_Methane_D4_D6: x_flow_Methane_D4_D6 >= 0
 non_negativity_x_Methane_D6_D7: x_flow_Methane_D6_D7 >= 0
 non_negativity_x_Methane_D5_D8: x_flow_Methane_D5_D8 >= 0
 non_negativity_x_Methane_D5_D9: x_flow_Methane_D5_D9 >= 0
 non_negativity_x_Methane_D9_D10: x_flow_Methane_D9_D10 >= 0
 non_negativity_x_Methane_D7_D10: x_flow_Methane_D7_D10 >= 0
 non_negativity_x_Methane_shortage_S1_S1: x_flow_Methane_shortage_S1_S1
   >= 0
 non_negativity_x_Methane_shortage_S2_S2: x_flow_Methane_shortage_S2_S2
   >= 0
 non_negativity_x_Methane_shortage_S3_S3: x_flow_Methane_shortage_S3_S3
   >= 0
 non_negativity_x_Hydrogen_S1_D1: x_flow_Hydrogen_S1_D1 >= 0
 non_negativity_x_Hydrogen_S1_D2: x_flow_Hydrogen_S1_D2 >= 0
 non_negativity_x_Hydrogen_S2_D2: x_flow_Hydrogen_S2_D2 >= 0
 non_negativity_x_Hydrogen_S2_D3: x_flow_Hydrogen_S2_D3 >= 0
 non_negativity_x_Hydrogen_S3_D1: x_flow_Hydrogen_S3_D1 >= 0
 non_negativity_x_Hydrogen_D1_D2: x_flow_Hydrogen_D1_D2 >= 0
 non_negativity_x_Hydrogen_D3_D4: x_flow_Hydrogen_D3_D4 >= 0
 non_negativity_x_Hydrogen_D4_D5: x_flow_Hydrogen_D4_D5 >= 0
 non_negativity_x_Hydrogen_D4_D6: x_flow_Hydrogen_D4_D6 >= 0
 non_negativity_x_Hydrogen_D6_D7: x_flow_Hydrogen_D6_D7 >= 0
 non_negativity_x_Hydrogen_D5_D8: x_flow_Hydrogen_D5_D8 >= 0
 non_negativity_x_Hydrogen_D5_D9: x_flow_Hydrogen_D5_D9 >= 0
 non_negativity_x_Hydrogen_D9_D10: x_flow_Hydrogen_D9_D10 >= 0
 non_negativity_x_Hydrogen_D7_D10: x_flow_Hydrogen_D7_D10 >= 0
 non_negativity_x_Hydrogen_shortage_S1_S1: x_flow_Hydrogen_shortage_S1_S1
   >= 0
 non_negativity_x_Hydrogen_shortage_S2_S2: x_flow_Hydrogen_shortage_S2_S2
   >= 0
 non_negativity_x_Hydrogen_shortage_S3_S3: x_flow_Hydrogen_shortage_S3_S3
   >= 0
Bounds
Binaries
 change_Methane_S1_D1 change_Methane_S1_D2 change_Methane_S2_D2
 change_Methane_S2_D3 change_Methane_S3_D1 change_Methane_D1_D2
 change_Methane_D3_D4 change_Methane_D4_D5 change_Methane_D4_D6
 change_Methane_D6_D7 change_Methane_D5_D8 change_Methane_D5_D9
 change_Methane_D9_D10 change_Methane_D7_D10 change_Methane_shortage_S1_S1
 change_Methane_shortage_S2_S2 change_Methane_shortage_S3_S3
 change_Hydrogen_S1_D1 change_Hydrogen_S1_D2 change_Hydrogen_S2_D2
 change_Hydrogen_S2_D3 change_Hydrogen_S3_D1 change_Hydrogen_D1_D2
 change_Hydrogen_D3_D4 change_Hydrogen_D4_D5 change_Hydrogen_D4_D6
 change_Hydrogen_D6_D7 change_Hydrogen_D5_D8 change_Hydrogen_D5_D9
 change_Hydrogen_D9_D10 change_Hydrogen_D7_D10
 change_Hydrogen_shortage_S1_S1 change_Hydrogen_shortage_S2_S2
 change_Hydrogen_shortage_S3_S3
End
