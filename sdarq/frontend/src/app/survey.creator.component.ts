import { Component, Input, Output, EventEmitter, OnInit } from '@angular/core';
import * as SurveyKo from 'survey-knockout';
import * as SurveyCreator from 'survey-creator';
import * as widgets from 'surveyjs-widgets';

import 'inputmask/dist/inputmask/phone-codes/phone.js';

widgets.icheck(SurveyKo);
widgets.select2(SurveyKo);
widgets.inputmask(SurveyKo);
widgets.jquerybarrating(SurveyKo);
widgets.jqueryuidatepicker(SurveyKo);
widgets.nouislider(SurveyKo);
widgets.select2tagbox(SurveyKo);
widgets.signaturepad(SurveyKo);
widgets.sortablejs(SurveyKo);
widgets.ckeditor(SurveyKo);
widgets.autocomplete(SurveyKo);
widgets.bootstrapslider(SurveyKo);
// widgets.emotionsratings(SurveyKo);

SurveyCreator.StylesManager.applyTheme('default');

const CkEditor_ModalEditor = {
  afterRender: function(modalEditor, htmlElement) {
    const editor = window['CKEDITOR'].replace(htmlElement);
    editor.on('change', function() {
      modalEditor.editingValue = editor.getData();
    });
    editor.setData(modalEditor.editingValue);
  },
  destroy: function(modalEditor, htmlElement) {
    const instance = window['CKEDITOR'].instances[htmlElement.id];
    if (instance) {
      instance.removeAllListeners();
      window['CKEDITOR'].remove(instance);
    }
  }
};
SurveyCreator.SurveyPropertyModalEditor.registerCustomWidget(
  'html',
  CkEditor_ModalEditor
);

@Component({
  // tslint:disable-next-line:component-selector
  selector: 'survey-creator',
  template: `
    <div id="surveyCreatorContainer"></div>
  `
})
export class SurveyCreatorComponent implements OnInit {
  surveyCreator: SurveyCreator.SurveyCreator;
  @Input() json: any;
  @Output() surveySaved: EventEmitter<Object> = new EventEmitter();
  ngOnInit() {
    SurveyKo.JsonObject.metaData.addProperty(
      'questionbase',
      'popupdescription:text'
    );
    SurveyKo.JsonObject.metaData.addProperty('page', 'popupdescription:text');

    const options = { showEmbededSurveyTab: true, generateValidJSON: true };
    this.surveyCreator = new SurveyCreator.SurveyCreator(
      'surveyCreatorContainer',
      options
    );
    this.surveyCreator.text = JSON.stringify(this.json);
    this.surveyCreator.saveSurveyFunc = this.saveMySurvey;
  }

  saveMySurvey = () => {
    console.log(JSON.stringify(this.surveyCreator.text));
    this.surveySaved.emit(JSON.parse(this.surveyCreator.text));
  };
}
