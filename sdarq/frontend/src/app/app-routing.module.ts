import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { MainpageComponent } from './mainpage/mainpage.component';
import { FormComponent} from './form/form.component';
import { NonDSPformComponent} from './non-dspform/non-dspform.component';
import { HomepageComponent } from './homepage/homepage.component';
import { CisComponent } from './cis/cis.component';
import { ScanpageComponent } from './scanpage/scanpage.component';


const routes: Routes = [
  { path: '', component: HomepageComponent},
  { path: 'newservice', component: MainpageComponent},
  { path: 'questionnaire', component: FormComponent},
  { path: 'notdspquestionnaire', component: NonDSPformComponent},
  { path: 'cis/scan', component: CisComponent},
  { path: 'scan', component: ScanpageComponent}
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
