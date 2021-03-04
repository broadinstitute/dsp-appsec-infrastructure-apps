import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { MainpageComponent } from './mainpage/mainpage.component';
import { FormComponent } from './form/form.component';
import { NonDSPformComponent } from './non-dspform/non-dspform.component';
import { HomepageComponent } from './homepage/homepage.component';
import { CisComponent } from './cis/cis.component';
import { ScanpageComponent } from './scanpage/scanpage.component';
import { CisResultsComponent } from './cis-results/cis-results.component';
import { CisScanComponent } from './cis-scan/cis-scan.component';
import { CisLandingPageComponent } from './cis-landing-page/cis-landing-page.component';
import { JiraTicketRiskAssesmentComponent } from './jira-ticket-risk-assesment/jira-ticket-risk-assesment.component';
import { ThreatModelComponent} from './threat-model/threat-model.component'
import { AboutPageComponent } from './about-page/about-page.component'
import { ServiceScanComponent } from './service-scan/service-scan.component'
import { MultiScanComponent } from './multi-scan/multi-scan.component';



const routes: Routes = [
  { path: '', component: HomepageComponent },
  { path: 'about', component: AboutPageComponent },
  { path: 'newservice', component: MainpageComponent },
  { path: 'questionnaire', component: FormComponent },
  { path: 'notdspquestionnaire', component: NonDSPformComponent },
  { path: 'cis/latest', component: CisComponent },
  { path: 'scan', component: ScanpageComponent },
  { path: 'cis/results', component: CisResultsComponent },
  { path: 'cis/scan', component: CisScanComponent },
  { path: 'cis', component: CisLandingPageComponent },
  { path: 'jira-ticket-risk-assesment', component: JiraTicketRiskAssesmentComponent },
  { path: 'threat-model/request', component: ThreatModelComponent },
  { path: 'scan-service', component: ServiceScanComponent},
  { path: 'multi-scan', component: MultiScanComponent}
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
