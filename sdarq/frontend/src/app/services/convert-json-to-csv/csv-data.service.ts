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
    const csv = (Json2csvParser(JSON.parse(data), {opts}).split(/"",""/gm).join('\n')).split(/""]/gm).join('').split(/\[""/gm).join('')
    return csv
  }

  exportToCsv(filename: string, csvContent: string) {
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
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