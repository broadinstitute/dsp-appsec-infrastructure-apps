import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';

import { AppComponent } from './app.component';
import { SurveyComponent } from './survey.component';
import { SurveyCreatorComponent } from './survey.creator.component';
import { FormComponent } from './form/form.component';
import { MainpageComponent } from './mainpage/mainpage.component';
import { AppRoutingModule } from './app-routing.module';
import { SendFormDataService } from './send-form-data.service';
import { HttpModule } from '@angular/http';
import { NonDSPformComponent } from './non-dspform/non-dspform.component';
import { HomepageComponent } from './homepage/homepage.component';


@NgModule({
  declarations: [
    AppComponent,
    SurveyComponent,
    SurveyCreatorComponent,
    FormComponent,
    MainpageComponent,
    NonDSPformComponent,
    HomepageComponent
  ],
  imports: [
    BrowserModule,
    FormsModule,
    HttpClientModule,
    AppRoutingModule,
    HttpModule
  ],
  providers: [
    SendFormDataService
  ],
  bootstrap: [
    AppComponent
  ]
})
export class AppModule {}
