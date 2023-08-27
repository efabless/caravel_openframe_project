#include <openframe.h>

/*
 * SPDX-FileCopyrightText: 2020 Efabless Corporation
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 * SPDX-License-Identifier: Apache-2.0
 */

void main(){
    for (int i = 0; i < 36; i++){
        GPIO_Configure(i, GPIO_MODE_VECTOR_OUTPUT);
    }
    GPIO_Configure(43, GPIO_MODE_VECTOR_OUTPUT);
    set_debug_reg1(0xAA);
    // timer one shot
   timer1_oneshot_config(0,0x5FFF);
   monitor_timer1_until(0xA1);
   timer1_oneshot_config(1,0x5FFF);
   monitor_timer1_until(0xA2);
   timer1_periodic_config(0,0x2FFF);
   monitor_timer1_until(0xA3);
   timer1_periodic_config(1,0x2FFF);
   monitor_timer1_until(0xA4);
}

void monitor_timer1_until(int stop_code){
    while (get_debug_reg2() != stop_code){
        int val = timer1_get_data();
        set_debug_reg1(val);
        GPIO_Set(val);
    }
}