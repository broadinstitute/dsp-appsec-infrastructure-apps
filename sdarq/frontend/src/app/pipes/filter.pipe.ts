import { Pipe, PipeTransform, Injectable } from '@angular/core';

@Pipe({
    name: 'filter',
})
@Injectable()
export class FilterPipe implements PipeTransform {
    transform(value: any[], searchString: string): any[] {
        if (!searchString) {
            return value;
        }
        if (searchString) {
            return value.filter((it) => {
                const id = it.id.toString().includes(searchString);
                const level = it.level.toString().includes(searchString);
                const cvss = it.cvss.toString().includes(searchString);
                const title = it.title
                    .toLowerCase()
                    .includes(searchString.toLowerCase());
                const description = it.description
                    .toLowerCase()
                    .includes(searchString.toLowerCase());
                const rationale = it.rationale
                    .toLowerCase()
                    .includes(searchString.toLowerCase());
                const benchmark = it.benchmark
                    .toLowerCase()
                    .includes(searchString.toLowerCase());
                return id + level + cvss + title + description + rationale + benchmark;
            });
        }
    }
}
