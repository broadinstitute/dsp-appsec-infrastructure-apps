import { Pipe, PipeTransform, Injectable } from '@angular/core';

@Pipe({
    name: 'filtersct',
})
@Injectable()
export class FiltersctPipe implements PipeTransform {
    transform(value: any[], searchString: string): any[] {
        if (!searchString) {
            return value;
        }
        if (searchString) {
            return value.filter((it) => {
                const service = it.service.toLowerCase().includes(searchString.toLowerCase());
                const product = it.product.toLowerCase().includes(searchString.toLowerCase());
                return service + product;
            });
        }
    }
}
