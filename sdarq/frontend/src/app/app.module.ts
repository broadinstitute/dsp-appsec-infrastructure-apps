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
import { SendFormDataService } from './send-form-data.service';
import { NonDSPformComponent } from './non-dspform/non-dspform.component';
import { HomepageComponent } from './homepage/homepage.component';
import { CisComponent } from './cis/cis.component';
import { CisProjectService} from './cis-project.service';


@NgModule({
  declarations: [
    AppComponent,
    SurveyComponent,
    SurveyCreatorComponent,
    FormComponent,
    MainpageComponent,
    NonDSPformComponent,
    HomepageComponent,
    CisComponent
  ],
  imports: [
    BrowserModule,
    FormsModule,
    HttpClientModule,
    AppRoutingModule,
    ReactiveFormsModule
  ],
  providers: [
    SendFormDataService,
    CisProjectService
    ],
  bootstrap: [
    AppComponent
  ]
})
export class AppModule {}
