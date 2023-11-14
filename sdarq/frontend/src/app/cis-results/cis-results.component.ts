import { ChangeDetectorRef, Component, NgZone, OnInit, ViewChildren, QueryList } from '@angular/core';
import { GetCisScanService } from '../services/get-project-cis-results/get-cis-scan.service';
import { ActivatedRoute } from '@angular/router';
import { CsvDataService } from '../services/convert-json-to-csv/csv-data.service';

import { Directive, EventEmitter, Input, Output } from '@angular/core';
import { CISfindings} from '../models/gcp-project-cis-findings.model'

export type SortColumn = keyof CISfindings | '';
export type SortDirection = 'asc' | 'desc' | '';


const rotate: { [key: string]: SortDirection } = {
  asc: 'desc',
  desc: '',
  '': 'asc',
};

export const compare = (
  v1: string | number | boolean | Date | string[],
  v2: string | number | boolean | Date | string[]
) => (v1 < v2 ? -1 : v1 > v2 ? 1 : 0);

export interface SortEvent {
  column: SortColumn;
  direction: SortDirection;
}

@Directive({
  selector: 'th[sortable]',
  host: {
    '[class.asc]': 'direction === "asc"',
    '[class.desc]': 'direction === "desc"',
    '(click)': 'rotate()',
  },
})

export class SortableHeaderDirective {
  @Input() sortable: SortColumn = '';
  @Input() direction: SortDirection = '';
  @Output() sort = new EventEmitter<SortEvent>();

  rotate() {
    this.direction = rotate[this.direction];
    this.sort.emit({ column: this.sortable, direction: this.direction });
  }
}

@Component({
  selector: 'app-cis-results',
  templateUrl: './cis-results.component.html',
  styleUrls: ['./cis-results.component.css']
})
export class CisResultsComponent implements OnInit {

  result: any;
  projectFindings: any[];
  params: any;
  value: string;
  showModal: boolean;
  showSpinner: boolean;
  errors: string;
  showTable: boolean;
  filename: string;
  projectId: string;
  updateDate: Date;
  headElements = ['Benchmark', 'Id', 'Level', 'CVSS', 'Title', 'Failures', 'Description', 'Rationale', 'Refs'];


  @Input() sortable: SortColumn = '';
  @Input() direction: SortDirection = '';
  @Output() sort = new EventEmitter<SortEvent>();


  @ViewChildren(CisResultsComponent) headers: QueryList<CisResultsComponent>;

  cisfinding: Array<CISfindings>
  data: Array<CISfindings> 


  constructor(private getProjectScan: GetCisScanService,
              private router: ActivatedRoute,
              private csvService: CsvDataService,
              private ngZone: NgZone,
              private ref: ChangeDetectorRef) {
                // This is intentional
               }

  ngOnInit() {
    this.showSpinner = true;
    this.router.queryParams.subscribe(params => {
      this.value = params.project_id
      this.getResults(this.value)
    })
  }

  saveAsCSV(projectFindings, updateDate, projectId) {
    this.filename = ['GCP_CIS_Results_', projectId, '_', updateDate.toISOString(), '.csv'].join('');
    const csvContent = this.csvService.ConvertToCSV(JSON.stringify(projectFindings), this.headElements);
    this.csvService.exportToCsv(this.filename, csvContent);
  }

  onSort({ column, direction }: SortEvent, cisfinding: Array<CISfindings>, data: Array<CISfindings> ) {
    this.headers.forEach((header) => {
      if (header.sortable !== column) {
        header.direction = '';
      }
    });

    if (direction === '' || column === '') {
      this.cisfinding = this.data;
    } else {
      this.cisfinding = [...this.data].sort((a, b) => {
        const res = compare(a[column], b[column]);
        return direction === 'asc' ? res : -res;
      });
    }
  }

  private getResults(value) {
    this.getProjectScan.getCisScan(this.value).subscribe((datas) => {
      this.ref.detectChanges();
      this.projectId = datas.meta.projectId;
      this.updateDate = new Date(datas.meta.lastModifiedDatetime);
      this.showSpinner = false;
      this.showTable = true;
      this.data = datas.findings;
      this.cisfinding = datas.findings;
    },
      (datas) => {
        this.ngZone.run(() => {
        this.showModal = true;
        this.errors = datas;
        this.showSpinner = false;
      });
    });
  }

}
