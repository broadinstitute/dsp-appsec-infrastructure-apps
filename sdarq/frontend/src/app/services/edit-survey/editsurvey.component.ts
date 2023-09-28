import { Component, Input, EventEmitter, Output, OnInit, SimpleChanges } from '@angular/core';
import * as Survey from 'survey-angular';
import * as widgets from 'surveyjs-widgets';
import * as SurveyPDF from 'survey-pdf';

widgets.icheck(Survey);
widgets.select2(Survey);
widgets.inputmask(Survey);
widgets.jquerybarrating(Survey);
widgets.jqueryuidatepicker(Survey);
widgets.nouislider(Survey);
widgets.select2tagbox(Survey);
widgets.sortablejs(Survey);
widgets.ckeditor(Survey);
widgets.autocomplete(Survey);
widgets.bootstrapslider(Survey);
widgets.prettycheckbox(Survey);

Survey.JsonObject.metaData.addProperty('questionbase', 'popupdescription:text');
Survey.JsonObject.metaData.addProperty('page', 'popupdescription:text');

Survey.StylesManager.applyTheme('default');


@Component({
  selector: 'app-editsurvey',
  template: `<div class='survey-container contentcontainer codecontainer '><div id='surveyElement'></div><button class="saveResponses" *ngIf="showPDFButton" (click)='savePDF()'>Save your answers</button></div>`

})
export class EditSurveyComponent implements OnInit {
  @Output() submitSurvey = new EventEmitter<any>();
  @Input() json: object;
  @Input() answers: object;
  result: any;
  showPDFButton: false;
  arrRequired: object;
  surveyModel: any;

  ngOnInit() {
    const surveyModel = new Survey.Model(this.json);
    this.surveyModel = surveyModel;
    
    surveyModel.onAfterRenderQuestion.add((survey, options) => {
      if (!options.question.popupdescription) { return; }
      const btn = document.createElement('button');
      btn.className = 'btn btn-info btn-xs';
      btn.innerHTML = 'More Info';
      btn.onclick = function () {
        alert(options.question.popupdescription);
      };
      const header = options.htmlElement.querySelector('h5');
      const span = document.createElement('span');
      span.innerHTML = '  ';
      header.appendChild(span);
      header.appendChild(btn);
    });
    surveyModel.onComplete
      .add((result, options) => {
        this.submitSurvey.emit(result.data);
        this.result = result.data;
        // @ts-ignore
          this.showPDFButton = true;
      });
    Survey.SurveyNG.render('surveyElement', { model: surveyModel });
  }

  ngOnChanges(changes: SimpleChanges) {
    for (const propName in changes) {
      if (propName ==  "answers")
      {
        if (changes[propName].currentValue)
        {
          this.surveyModel.data = changes[propName].currentValue;
        }
      }
    }
  }

  savePDF() {
    const options = {
      fontSize: 11,
      margins: {
        left: 5,
        right: 5,
        top: 10,
        bot: 10
      }
    };
    const surveyPDF = new SurveyPDF.SurveyPDF(this.json, options);
    surveyPDF.data = this.result;
    surveyPDF.save('completed_form');
  }
}