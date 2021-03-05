import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { AppComponent } from './app.component';
import { SurveyComponent } from './survey.component';
import { SurveyCreatorComponent } from './survey.creator.component';
import { FormComponent } from './form/form.component';
import { MainpageComponent } from './mainpage/mainpage.component';
import { AppRoutingModule } from './app-routing.module';
import { SendFormDataService } from './services/send-form-data.service';
import { NonDSPformComponent } from './non-dspform/non-dspform.component';
import { HomepageComponent } from './homepage/homepage.component';
import { CisComponent } from './cis/cis.component';
import { CisProjectService } from './services/cis-project.service';
import { MDBBootstrapModule } from 'angular-bootstrap-md';
import { NavbarComponent } from './navbar/navbar.component';
import { ScanpageComponent } from './scanpage/scanpage.component';
import { GetCisScanService } from './services/get-cis-scan.service';
import { FooterComponent } from './footer/footer.component';
import { CisResultsComponent } from './cis-results/cis-results.component';
import { CisScanComponent } from './cis-scan/cis-scan.component';
import { CisLandingPageComponent } from './cis-landing-page/cis-landing-page.component';
import { FilterPipe } from './pipes/filter.pipe';
import { JiraTicketRiskAssesmentComponent } from './jira-ticket-risk-assesment/jira-ticket-risk-assesment.component';
import { ThreatModelComponent } from './threat-model/threat-model.component';
import { RequestTmService} from './services/request-tm.service';
import { AboutPageComponent } from './about-page/about-page.component'
import { CsvDataService } from './services/csv-data.service';
import { ServiceScanComponent } from './service-scan/service-scan.component'
import { ScanServiceService} from './services/scan-service.service';
import { MultiScanComponent } from './multi-scan/multi-scan.component';
import { NotfoundComponent } from './notfound/notfound.component';



@NgModule({
  declarations: [
    AppComponent,
    SurveyComponent,
    SurveyCreatorComponent,
    FormComponent,
    MainpageComponent,
    NonDSPformComponent,
    HomepageComponent,
    CisComponent,
    NavbarComponent,
    ScanpageComponent,
    FooterComponent,
    CisResultsComponent,
    CisScanComponent,
    CisLandingPageComponent,
    FilterPipe,
    JiraTicketRiskAssesmentComponent,
    ThreatModelComponent,
    AboutPageComponent,
    ServiceScanComponent,
    MultiScanComponent,
    NotfoundComponent
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
    ScanServiceService
    ],
  bootstrap: [
    AppComponent
  ],
  exports: [
    FilterPipe
  ]
})
export class AppModule { }
