//
//  ViewController.m
//  cardGroupTableDemo
//
//  Created by iOS1 on 2022/10/24.
//  Copyright © 2022 Developer. All rights reserved.
//



#import "ViewController.h"
#import "GroupShadowTableView.h"

@interface ViewController () <GroupShadowTableViewDelegate,GroupShadowTableViewDataSource>
@property (weak, nonatomic) IBOutlet GroupShadowTableView *tableView;

@end

@implementation ViewController

- (void)viewDidLoad {
    [super viewDidLoad];
    // Do any additional setup after loading the view, typically from a nib.
    
    //self.tableView.backgroundColor = [UIColor groupTableViewBackgroundColor];
    self.tableView.groupShadowDelegate = self;
    self.tableView.groupShadowDataSource = self;
    self.tableView.showSeparator = YES;
   
}


- (void)didReceiveMemoryWarning {
    [super didReceiveMemoryWarning];
    // Dispose of any resources that can be recreated.
}

//MARK: - GroupShadowTableViewDataSource
- (NSInteger)numberOfSectionsInGroupShadowTableView:(GroupShadowTableView *)tableView {
    return 5;
}

- (NSInteger)groupShadowTableView:(GroupShadowTableView *)tableView numberOfRowsInSection:(NSInteger)section {
    return 4;
}

- (UITableViewCell *)groupShadowTableView:(GroupShadowTableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {
    UITableViewCell *cell = [tableView dequeueReusableCellWithIdentifier:@"Cell"];
    cell.textLabel.text = [NSString stringWithFormat:@"section -> %@ ; row -> %@",@(indexPath.section) ,@(indexPath.row)];
    return cell;
    
}


//MARK: - GroupShadowTableViewDelegate
- (CGFloat)groupShadowTableView:(GroupShadowTableView *)tableView heightForRowAtIndexPath:(NSIndexPath *)indexPath {
    return 60;
}

- (void)groupShadowTableView:(GroupShadowTableView *)tableView didSelectRowAtIndexPath:(NSIndexPath *)indexPath {
    [tableView deselectRowAtIndexPath:indexPath animated:YES];

}
//头部高度
- (CGFloat)groupShadowTableView:(GroupShadowTableView *)tableView heightForHeaderInSection:(NSInteger)section {
    return 40.f;
}

//头部view
- (UIView *)groupShadowTableView:(GroupShadowTableView *)tableView viewForHeaderInSection:(NSInteger)section {
    
    UIView *sectionView = [[UIView alloc]initWithFrame:CGRectZero];
    //sectionView.backgroundColor = [UIColor groupTableViewBackgroundColor];
    
    UILabel *label = [[UILabel alloc]init];
    label.textColor = [UIColor blackColor];
    label.text = [NSString stringWithFormat:@"我是头%zd",section];
    label.frame = CGRectMake(16,8,[UIScreen mainScreen].bounds.size.width-16, 16);
    [sectionView addSubview:label];
    
      return sectionView;
}

//尾部高度
- (CGFloat)groupShadowTableView:(GroupShadowTableView *)tableView heightForFooterInSection:(NSInteger)section {
    
    return 30.f;
}

//尾部view
- (UIView *)groupShadowTableView:(GroupShadowTableView *)tableView viewForFooterInSection:(NSInteger)section {
    
    UIView *sectionView = [[UIView alloc]initWithFrame:CGRectZero];
    //sectionView.backgroundColor = [UIColor groupTableViewBackgroundColor];
    UILabel *label = [[UILabel alloc]init];
    label.textColor = [UIColor blackColor];
    label.text = [NSString stringWithFormat:@"我是尾%zd",section];
    label.frame = CGRectMake(16,8, [UIScreen mainScreen].bounds.size.width-16, 16);
    [sectionView addSubview:label];
    
      return sectionView;
}

@end
