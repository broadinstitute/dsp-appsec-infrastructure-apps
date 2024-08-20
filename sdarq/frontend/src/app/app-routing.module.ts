import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { MainpageComponent } from './mainpage/mainpage.component';
import { FormComponent } from './form/form.component';
import { HomepageComponent } from './homepage/homepage.component';
import { CisComponent } from './cis/cis.component';
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
import { SecurityRequestsComponent } from './security-requests/security-requests.component';
import { SecurityControlsComponent } from './security-controls/security-controls.component';
import { AppFormComponent } from './app-form/app-form.component';
import { AppsMainpageComponent } from './apps-mainpage/apps-mainpage.component';
import { SearchServiceSecurityControlsComponent } from './search-service-security-controls/search-service-security-controls.component';
import { DeleteServiceSecurityControlsComponent } from './delete-service-security-controls/delete-service-security-controls.component';
import { AuthzGuard } from './authz.guard';
import { TerraNewServiceComponent } from './terra-new-service/terra-new-service.component';


const routes: Routes = [
  { path: '', component: HomepageComponent },
  { path: 'about', component: AboutPageComponent },
  { path: 'TerraNewService', component: MainpageComponent },
  { path: 'questionnaire', component: TerraNewServiceComponent },
  { path: 'generalServiceQuestionnaire', component: FormComponent },
  { path: '3rd-party-app-questionnaire', component: AppFormComponent },
  { path: 'new-3rd-party-app', component: AppsMainpageComponent },
  { path: 'gcp-project-security-posture/latest', component: CisComponent },
  { path: 'gcp-project-security-posture/results', component: CisResultsComponent },
  { path: 'gcp-project-security-posture/scan', component: CisScanComponent },
  { path: 'gcp-project-security-posture', component: CisLandingPageComponent },
  { path: 'jira-ticket-risk-assesment', component: JiraTicketRiskAssesmentComponent },
  { path: 'threat-model/request', component: ThreatModelComponent },
  { path: 'scan-service', component: ServiceScanComponent },
  { path: 'security-requests', component: SecurityRequestsComponent },
  { path: 'security-controls', component: SecurityControlsComponent },
  { path: 'security-control/create', component: SecurityControlsFormComponent, canActivate: [AuthzGuard] },
  { path: 'security-control/view', component: SecurityControlsListComponent },
  { path: 'security-control/edit', component: EditSecurityControlsFormComponent, canActivate: [AuthzGuard] },
  { path: 'security-pentest/request', component: SecurityPentestComponent },
  { path: 'search-service-security-controls', component: SearchServiceSecurityControlsComponent },
  { path: 'security-control/delete-service', component: DeleteServiceSecurityControlsComponent, canActivate: [AuthzGuard] },
  { path: '404', component: NotfoundComponent },
  { path: '**', redirectTo: '/404' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
