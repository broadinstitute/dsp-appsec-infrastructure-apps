import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { MDBBootstrapModule } from 'angular-bootstrap-md';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { AppComponent } from './app.component';
import { SurveyComponent } from './services/survejs-form/survey.component';
import { SurveyCreatorComponent } from './services/survejs-form/survey.creator.component';
import { FormComponent } from './form/form.component';
import { MainpageComponent } from './mainpage/mainpage.component';
import { HomepageComponent } from './homepage/homepage.component';
import { CisComponent } from './cis/cis.component';
import { NavbarComponent } from './navbar/navbar.component';
import { FooterComponent } from './footer/footer.component';
import { CisResultsComponent } from './cis-results/cis-results.component';
import { CisScanComponent } from './cis-scan/cis-scan.component';
import { CisLandingPageComponent } from './cis-landing-page/cis-landing-page.component';
import { JiraTicketRiskAssesmentComponent } from './jira-ticket-risk-assesment/jira-ticket-risk-assesment.component';
import { ThreatModelComponent } from './threat-model/threat-model.component';
import { AboutPageComponent } from './about-page/about-page.component'
import { ServiceScanComponent } from './service-scan/service-scan.component'
import { NotfoundComponent } from './notfound/notfound.component';
import { SecurityControlsFormComponent } from './security-controls-form/security-controls-form.component';
import { SecurityControlsListComponent } from './security-controls-list/security-controls-list.component';
import { EditSecurityControlsFormComponent } from './edit-security-controls-form/edit-security-controls-form.component';
import { SecurityPentestComponent } from './security-pentest/security-pentest.component';
import { SecurityRequestsComponent } from './security-requests/security-requests.component';
import { SecurityControlsComponent } from './security-controls/security-controls.component';
import { GetSecurityControlsService } from './services/get-all-security-controls/get-security-controls.service';
import { CreateNewSctService } from './services/create-new-security-controls/create-new-sct.service';
import { ScanServiceService } from './services/scan-service/scan-service.service';
import { CsvDataService } from './services/convert-json-to-csv/csv-data.service';
import { RequestTmService } from './services/threat-model-request/request-tm.service';
import { GetCisScanService } from './services/get-project-cis-results/get-cis-scan.service';
import { CisProjectService } from './services/scan-gcp-project/cis-project.service';
import { GetServiceSecurityControlsService } from './services/get-service-security-controls/get-service-security-controls.service';
import { SendFormDataService } from './services/create-new-service/send-form-data.service';
import { EditSecurityControlsService } from './services/edit-service-security-controls/edit-security-controls.service';
import { RequestSecurityPentestService } from './services/security-pentest-request/request-security-pentest.service';
import { JiraTicketRiskAssessmentService } from './services/jira-ticket-risk-assessment/jira-ticket-risk-assessment.service';
import { SendAppFormDataService } from './services/create-new-app/send-app-form-data.service';
import { FilterPipe } from './pipes/filter.pipe';
import { FiltersctPipe } from './pipes/filtersct.pipe';
import { AppRoutingModule } from './app-routing.module';
import { AppFormComponent } from './app-form/app-form.component';
import { AppsMainpageComponent } from './apps-mainpage/apps-mainpage.component';
import { ServiceSecurityControlsComponent } from './service-security-controls/service-security-controls.component';
import { SearchServiceSecurityControlsComponent } from './search-service-security-controls/search-service-security-controls.component';
import { DeleteServiceSecurityControlsComponent } from './delete-service-security-controls/delete-service-security-controls.component';
import { DeleteServiceSecurityControlsService } from './services/delete-service-security-controls/delete-service-security-controls.service';
import { TerraNewServiceComponent } from './terra-new-service/terra-new-service.component';
import { SortableHeaderDirective } from './cis-results/cis-results.component';
import { AuthzService } from './services/authz/authz.service';



@NgModule({
  declarations: [
    AppComponent,
    SortableHeaderDirective,
    SurveyComponent,
    SurveyCreatorComponent,
    FormComponent,
    MainpageComponent,
    HomepageComponent,
    CisComponent,
    NavbarComponent,
    FooterComponent,
    CisResultsComponent,
    CisScanComponent,
    CisLandingPageComponent,
    FilterPipe,
    FiltersctPipe,
    JiraTicketRiskAssesmentComponent,
    ThreatModelComponent,
    AboutPageComponent,
    ServiceScanComponent,
    NotfoundComponent,
    SecurityControlsFormComponent,
    SecurityControlsListComponent,
    EditSecurityControlsFormComponent,
    SecurityPentestComponent,
    SecurityRequestsComponent,
    SecurityControlsComponent,
    AppFormComponent,
    AppsMainpageComponent,
    ServiceSecurityControlsComponent,
    SearchServiceSecurityControlsComponent,
    DeleteServiceSecurityControlsComponent,
    TerraNewServiceComponent
    ],
  imports: [
    BrowserModule, 
    FormsModule,
    HttpClientModule,
    AppRoutingModule,
    ReactiveFormsModule,
    BrowserAnimationsModule,
    MDBBootstrapModule.forRoot()
  ],
  providers: [
    SendFormDataService,
    CisProjectService,
    GetCisScanService,
    RequestTmService,
    CsvDataService,
    ScanServiceService,
    CreateNewSctService,
    GetSecurityControlsService,
    EditSecurityControlsService,
    GetServiceSecurityControlsService,
    RequestSecurityPentestService,
    JiraTicketRiskAssessmentService,
    SendAppFormDataService,
    DeleteServiceSecurityControlsService,
    AuthzService
    ],
  bootstrap: [
    AppComponent
  ],
  exports: [
    FilterPipe,
    FiltersctPipe
  ]
})
export class AppModule { }
