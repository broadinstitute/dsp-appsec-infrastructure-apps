import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { MainpageComponent } from './mainpage/mainpage.component';
import { FormComponent } from './form/form.component';
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
import { NotfoundComponent} from './notfound/notfound.component'
import { SecurityControlsFormComponent} from './security-controls-form/security-controls-form.component'
import { SecurityControlsListComponent } from './security-controls-list/security-controls-list.component';
import { EditSecurityControlsFormComponent } from './edit-security-controls-form/edit-security-controls-form.component';
import { SecurityPentestComponent } from './security-pentest/security-pentest.component';



const routes: Routes = [
  { path: '', component: HomepageComponent },
  { path: 'about', component: AboutPageComponent },
  { path: 'newservice', component: MainpageComponent },
  { path: 'questionnaire', component: FormComponent },
  { path: 'scan', component: ScanpageComponent },
  { path: 'cis/latest', component: CisComponent },
  { path: 'cis/results', component: CisResultsComponent },
  { path: 'cis/scan', component: CisScanComponent },
  { path: 'cis', component: CisLandingPageComponent },
  { path: 'jira-ticket-risk-assesment', component: JiraTicketRiskAssesmentComponent },
  { path: 'threat-model/request', component: ThreatModelComponent },
  { path: 'scan-service', component: ServiceScanComponent },
  { path: 'security-control/create', component: SecurityControlsFormComponent },
  { path: 'security-control/view', component: SecurityControlsListComponent },
  { path: 'security-control/edit', component: EditSecurityControlsFormComponent },
  { path: 'security-pentest/request', component: SecurityPentestComponent },
  { path: '404', component: NotfoundComponent },
  { path: '**', redirectTo: '/404' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
