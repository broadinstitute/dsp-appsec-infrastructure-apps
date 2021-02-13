import { Injectable } from '@angular/core';
declare var require: any

@Injectable({
  providedIn: 'root'
})
export class CsvDataService {

  ConvertToCSV(data: string, fieldsdata: any): string {
    const Json2csvParser = require('json2csv').parse;
    const fields = fieldsdata;
    const opts = { fields };
    const csv_notformatted = Json2csvParser(JSON.parse(data), {opts});
    const csv_format = csv_notformatted.split(/"",""/gm).join('\n');
    const csv = csv_format.split(/""]/gm).join('').split(/\[""/gm).join('')
    return csv
  }

  exportToCsv(filename: string, csvContent: string) {
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    if (navigator.msSaveBlob) {
      navigator.msSaveBlob(blob, filename);
    } else {
      const link = document.createElement('a');
      if (link.download !== undefined) {
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', filename);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      }
    }
  }
}
