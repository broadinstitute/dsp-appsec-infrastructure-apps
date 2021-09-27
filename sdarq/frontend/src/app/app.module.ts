import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { MDBBootstrapModule } from 'angular-bootstrap-md';
// Listed components
import { AppComponent } from './app.component';
import { SurveyComponent } from './survey.component';
import { SurveyCreatorComponent } from './survey.creator.component';
import { FormComponent } from './form/form.component';
import { MainpageComponent } from './mainpage/mainpage.component';
import { HomepageComponent } from './homepage/homepage.component';
import { CisComponent } from './cis/cis.component';
import { NavbarComponent } from './navbar/navbar.component';
import { ScanpageComponent } from './scanpage/scanpage.component';
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
// Listed services
import { GetSecurityControlsService } from './services/get-security-controls.service';
import { CreateNewSctService } from './services/create-new-sct.service';
import { ScanServiceService } from './services/scan-service.service';
import { CsvDataService } from './services/csv-data.service';
import { RequestTmService } from './services/request-tm.service';
import { GetCisScanService } from './services/get-cis-scan.service';
import { CisProjectService } from './services/cis-project.service';
import { SendFormDataService } from './services/send-form-data.service';
import { EditSecurityControlsService } from './services/edit-security-controls.service';
// Listed pipes
import { FilterPipe } from './pipes/filter.pipe';
import { FiltersctPipe } from './pipes/filtersct.pipe';
// Router
import { AppRoutingModule } from './app-routing.module';


@NgModule({
  declarations: [
    AppComponent,
    SurveyComponent,
    SurveyCreatorComponent,
    FormComponent,
    MainpageComponent,
    HomepageComponent,
    CisComponent,
    NavbarComponent,
    ScanpageComponent,
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
    EditSecurityControlsFormComponent
    ],
  imports: [
    BrowserModule,
    FormsModule,
    HttpClientModule,
    AppRoutingModule,
    ReactiveFormsModule,
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
    EditSecurityControlsService
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
